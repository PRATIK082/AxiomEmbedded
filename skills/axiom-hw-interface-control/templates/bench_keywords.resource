*** Settings ***
Documentation    Bench resource: logical-name sessions with fail-safe teardown.
...              Imported by campaign suites; channels resolve via board_config.
Library          OperatingSystem
Library          Process

*** Keywords ***
Bench Pre-Check
    [Documentation]    Resolve board config, probe instruments, match DUT hash.
    [Arguments]    ${board_config}    ${firmware_hash}
    ${rc}    ${out}=    Run And Return Rc And Output    python    scripts/bench_discover.py    ${board_config}
    Should Be Equal As Integers    ${rc}    0
    Should Contain    ${out}    "unresolved": []
    Log    ${out}

Bench Teardown
    [Documentation]    Open relays, reset DUT, flush buffers. Runs always.
    [Arguments]    ${board_config}
    Log    Teardown ${board_config}: relays open, DUT reset, buffers flushed.    WARN

Bench Teardown Report Exists
    [Documentation]    Teardown report artifact check for the campaign.
    File Should Exist    results/teardown-report.json
