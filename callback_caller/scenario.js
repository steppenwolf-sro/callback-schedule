VoxEngine.addEventListener(AppEvents.Started, handleScenarioStart);

var url;
var callToClient;

var clientUnavailableTimeout;
var managerUnavailableTimeout;

var managerPhones;
var callsToManagers = [];
var clientStatusCallback;

var managerTimeout;

var entryUrl;

var recordUrl;

function handleScenarioStart() {
    var data = VoxEngine.customData().split("|");
    var clientPhone = data[0];
    var fromPhone = data[1];
    url = data[2];
    clientStatusCallback = data[3];
    var timeout = parseInt(data[4]) * 1000;

    Logger.write(JSON.stringify(PhoneNumber.getInfo(clientPhone)));
    if (!PhoneNumber.getInfo(clientPhone).isValidNumber) {
        terminateCall("wrong-number");
        return;
    }

    Logger.write(url);
    Logger.write(fromPhone);

    callToClient = VoxEngine.callPSTN(clientPhone);
    clientUnavailableTimeout = setTimeout(function () {
        Logger.write("Client answer timeout");
        clientDidNotAnswer();
    }, timeout);
    callToClient.addEventListener(CallEvents.Connected, handleCallToClientConnected);

    callToClient.addEventListener(CallEvents.Disconnected, callEnded);
    callToClient.addEventListener(CallEvents.Failed, clientDidNotAnswer);
    callToClient.addEventListener(CallEvents.VoicemailPromptDetected, clientDidNotAnswer);
}

function terminateCall(reason) {
    Net.httpRequestAsync(clientStatusCallback + "?DialCallStatus=" + reason)
        .then(function (response) {
            Logger.write("Server notified: " + reason + ". Terminating the call.");
            VoxEngine.terminate();
        });
}

function clientDidNotAnswer() {
    terminateCall("failed");
}

function handleCallToClientConnected() {
    clearTimeout(clientUnavailableTimeout);
    callToClient.record();
    callToClient.addEventListener(CallEvents.RecordStarted, recordStarted);

    Logger.write("Making request to " + url);
    Net.httpRequestAsync(url + "?client=voximplant").then(processResponse);
}

function processResponse(response) {
    var json = JSON.parse(response.text);
    Logger.write("Got response: " + response.text);

    if (json.next === 'hangup') {
        Logger.write("We've got a command to hang up");
        VoxEngine.terminate();
        return;
    }

    managerPhones = json.phones;
    Logger.write("We've got phones: " + JSON.stringify(managerPhones));

    managerTimeout = json.timeout * 1000;
    entryUrl = json.action;

    if (json.intro) {
        callToClient.addEventListener(CallEvents.PlaybackFinished, introPlayed);
        callToClient.startPlayback(json.intro, false);
    } else {
        startCallsToManagers();
    }
}

function recordStarted(data) {
    recordUrl = data.url;
}

function startCallsToManagers() {
    callsToManagers = [];
    for (var i = 0; i < managerPhones.length; i++) {
        var phone = managerPhones[i];
        var callToManager = VoxEngine.callPSTN(phone);
        callToManager.addEventListener(CallEvents.Connected, managerDidAnswer);

        callToManager.addEventListener(CallEvents.Disconnected, managerCompletedCall);

        callToManager.addEventListener(CallEvents.Failed, managerDidNotAnswer);
        callToManager.addEventListener(CallEvents.VoicemailPromptDetected, managerDidNotAnswer);
        callsToManagers.push(callToManager);
    }

    managerUnavailableTimeout = setTimeout(managersUnavailable, managerTimeout);
}

function introPlayed() {
    callToClient.playProgressTone("RU");

    startCallsToManagers();
}

function managerCompletedCall(data) {
    callToClient.hangup();
}

function managersUnavailable() {
    Net.httpRequestAsync(entryUrl + "?client=voximplant&DialCallStatus=no-answer").then(processResponse);
}

function managerDidNotAnswer(data) {
    var call = data.call;
    Logger.write(JSON.stringify(call));
    Logger.write(call.number() + " failed");

    for (var i = 0; i < callsToManagers.length; i++) {
        var item = callsToManagers[i];
        Logger.write(item.number() + " - " + item.state());
    }

    // TODO: if no PROGRESSING phones left, cancel managerUnavailableTimeout and call managersUnavailable
}

function managerDidAnswer(data) {
    clearTimeout(managerUnavailableTimeout);

    var call = data.call;

    for (var i = 0; i < callsToManagers.length; i++) {
        var item = callsToManagers[i];
        if (call != item) {
            item.hangup();
        }
    }

    VoxEngine.sendMediaBetween(callToClient, call);
}

function callEnded(data) {
    Logger.write("The call has ended");

    Net.httpRequestAsync(entryUrl + "?DialCallStatus=completed&RecordingUrl=" +
        recordUrl + "&RecordingDuration=" + data.duration)
        .then(function (response) {
            Logger.write("Server notified. Terminating the call.");
            VoxEngine.terminate();
        });
}