"use strict";

const QB = require("quickblox");
const fetch = require("node-fetch");

const CONFIG = {
  appId: "103167",
  authKey: "ak_uY5JEUGcAAbBpb5",
  authSecret: "as_fqTbyROThZpbDe6",
  accountKey: "ack_12eKCDzWhxiPCfGMHHTv", // Add your account key here
  botUser: {
    id: "139708831",
    password: "carey123",
  },
  chatgptEndpoint: "/chatgpt4/", // Update with your Django endpoint URL
};

// Initialise QuickBlox
QB.init(CONFIG.appId, CONFIG.authKey, CONFIG.authSecret, CONFIG.accountKey); //Callout your AccountKey here

// Connect to Real-Time Chat
QB.chat.connect(
  {
    userId: CONFIG.botUser.id,
    password: CONFIG.botUser.password,
  },
  (chatConnectError) => {
    if (chatConnectError) {
      console.log("[QB] chat.connect is failed", JSON.stringify(chatConnectError));
      process.exit(1);
    }

    console.log("[QB] Bot is up and running");

    // Add chat messages listener
    QB.chat.onMessageListener = onMessageListener;
  }
);

async function onMessageListener(userId, msg) {
  // process 1-1 messages
  if (msg.type == "chat" && msg.body) {
    try {
      const chatgptResponse = await fetch(CONFIG.chatgptEndpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: msg.body,
        }),
      });

      if (!chatgptResponse.ok) {
        throw new Error("Failed to process message");
      }

      const { reply } = await chatgptResponse.json();

      // Send the reply back to the user
      let answerMessage = {
        type: "chat",
        body: reply,
        extension: {
          save_to_history: 1,
        },
      };

      QB.chat.send(userId, answerMessage);
    } catch (error) {
      console.error("Error processing message:", error.message);
    }
  }
}

process.on("exit", function () {
  console.log("Kill bot");
  QB.chat.disconnect();
});