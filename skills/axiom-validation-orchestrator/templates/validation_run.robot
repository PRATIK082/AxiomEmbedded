*** Settings ***
Documentation    AxiomEmbedded validation campaign skeleton.
...              Fill Variables per campaign; bind Adapter by variable file.
...              Same suite runs with-harness (physical rig) and
...              without-harness (virtual ECU API); only variables change.
...              Self-contained: copy this one file into the target project.
...              Canonical rig keywords live in axiom-hw-interface-control
...              templates/bench_keywords.resource for shared benches.
Library          OperatingSystem

*** Variables ***
${BOARD_CONFIG}    board_config.yaml
${FIRMWARE_HASH}    SET-ME
${ADAPTER}         virtual
${RESULT_DIR}      results/${SUITE_NAME}

*** Test Cases ***
Pre-Check Bench Readiness
    [Documentation]    Instruments reachable, DUT rails present, hash matches.
    [Tags]    pre-check
    Bench Pre-Check    ${BOARD_CONFIG}    ${FIRMWARE_HASH}

Nominal Operation Passes
    [Documentation]    Positive case: requirement under nominal conditions.
    [Tags]    sil    hil
    Run Nominal Scenario    ${ADAPTER}

Boundary Rejection Holds
    [Documentation]    Negative case: out-of-range input rejected.
    [Tags]    sil    hil
    Run Boundary Scenario    ${ADAPTER}

Fault Injection Reaches Fail-Safe
    [Documentation]    Template: inject fault, assert declared safe state.
    [Tags]    sil    hil    fault
    Inject Fault And Assert Safe State    ${ADAPTER}    FAULT-NAME    SAFE-STATE

Fail-Safe Teardown Always Runs
    [Documentation]    Teardown report exists even after induced failure.
    [Tags]    teardown
    Bench Teardown Report Exists

*** Keywords ***
Run Nominal Scenario
    [Arguments]    ${adapter}
    Log    Bind campaign nominal steps to ${adapter} adapter.    WARN

Run Boundary Scenario
    [Arguments]    ${adapter}
    Log    Bind campaign boundary steps to ${adapter} adapter.    WARN

Inject Fault And Assert Safe State
    [Arguments]    ${adapter}    ${fault}    ${safe_state}
    Log    Inject ${fault} via ${adapter}; assert ${safe_state}.    WARN

Bench Pre-Check
    [Documentation]    Skeleton pre-check: board config present, DUT hash attested.
    ...    Rig campaigns should call Bench Pre-Check Passes from
    ...    axiom-hw-interface-control templates/bench_keywords.resource.
    [Arguments]    ${board_config}    ${firmware_hash}
    File Should Exist    ${board_config}
    Should Not Be Equal    ${firmware_hash}    SET-ME

Bench Teardown Report Exists
    [Documentation]    Teardown report exists even after induced failure.
    ...    The campaign teardown hook writes this file unconditionally.
    File Should Exist    ${RESULT_DIR}/teardown-report.json
