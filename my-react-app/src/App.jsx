import { useState, useEffect } from "react";
import axios from "axios";
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator,
} from "@chatscope/chat-ui-kit-react";
import { format } from "date-fns";

let counter = 0;
let isQuestion = false;

function App() {
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState([]);

  const handleSendMessage = async (message) => {
    setMessages((prev) => [
      ...prev,
      {
        message,
        sender: "You",
        direction: "outgoing",
      },
    ]);
    setIsTyping(true);

    try {
      const response = await axios.post("http://localhost:5000/api/message", {
        message,
        counter,
        isQuestion,
      });
      if (response.data?.question) {
        isQuestion = true;
      } else {
        isQuestion = false;
      }
      if (response.data?.counter) {
        counter = -1;
      }
      setMessages((prev) => [
        ...prev,
        {
          message: response.data.response,
          sender: "SuperMarket Bot",
          direction: "incoming",
        },
      ]);
    } catch (err) {
      console.log(err);
    } finally {
      setIsTyping(false);
      counter++;
    }
  };

  /*  useEffect(() => {
    const fetchInitialMessage = async () => {
      try {
        const response = await axios.post("http://localhost:5000/api/message");
        setMessages((prev) => [
          ...prev,
          {
            message: response.data.response,
            sender: "SuperMarket Bot",
            direction: "incoming",
          },
        ]);
      } catch (err) {
        console.log(err);
      }
    };
    fetchInitialMessage();
  }, []); */

  return (
    <div
      className="w-1/2 "
      style={{
        margin: "auto",
        height: "100vh",
      }}
    >
      <MainContainer>
        <ChatContainer>
          <MessageList
            typingIndicator={
              isTyping ? (
                <TypingIndicator content="SuperMarket Bot is typing..." />
              ) : null
            }
          >
            {messages.map((message, index) => (
              <Message
                model={{
                  key: index,
                  message: message.message,
                  sentTime: format(new Date(), "HH:mm"),
                  sender: message.sender,
                  direction: message.direction,
                }}
              />
            ))}
          </MessageList>
          <MessageInput
            placeholder="Type message here"
            onSend={handleSendMessage}
          />
        </ChatContainer>
      </MainContainer>
    </div>
  );
}

export default App;
