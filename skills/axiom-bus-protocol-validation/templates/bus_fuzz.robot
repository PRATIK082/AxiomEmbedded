*** Settings ***
Documentation    Protocol fuzz skeleton: malformed frames must reject or contain.
...              DUT must never crash, hang, or execute on fuzz input.
Library          OperatingSystem

*** Variables ***
${CORPUS_DIR}    fuzz/corpus
${CASE_BUDGET}   500

*** Test Cases ***
UART Malformed Lines Rejected
    [Documentation]    Oversized and break-injected lines rejected, console resyncs.
    [Tags]    security    sil    hil
    Run Fuzz Case    uart    ${CORPUS_DIR}/uart    ${CASE_BUDGET}

CAN Fuzz No Transmit Lockup
    [Documentation]    Random IDs and payloads; error accounting sane, no lockup.
    [Tags]    security    sil    hil
    Run Fuzz Case    can    ${CORPUS_DIR}/can    ${CASE_BUDGET}

MQTT Auth And Oversize Rejected
    [Documentation]    Bad credentials, ACL violation, oversize payload rejected.
    [Tags]    security    no-harness
    Run Fuzz Case    mqtt    ${CORPUS_DIR}/mqtt    ${CASE_BUDGET}

BLE Malformed GATT Rejected
    [Documentation]    Bad pairing and GATT ops rejected; link loss fails safe.
    [Tags]    security    hil
    Run Fuzz Case    ble    ${CORPUS_DIR}/ble    ${CASE_BUDGET}

*** Keywords ***
Run Fuzz Case
    [Arguments]    ${protocol}    ${corpus}    ${budget}
    Log    Fuzz ${protocol} with ${budget} cases from ${corpus}.    WARN
