import React, { useState, useEffect } from "react";
import api from "../api/axiosConfig";

export default function Transactions() {
  const [history, setHistory] = useState([]);
  const [receiver, setReceiver] = useState("");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");

  useEffect(() => {
    api.get("/transactions/history").then((res) => {
      setHistory(res.data);
    });
  }, []);

  const sendMoney = async () => {
    await api.post("/transactions/send", {
      receiverEmail: receiver,
      amount,
      description,
    });
    alert("Sent successfully");
  };

  const downloadStatement = async () => {
    const res = await api.get("/transactions/statement", {
      responseType: "blob",
    });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "statement.pdf");
    link.click();
  };

  return (
    <div>
      <h1>Transactions</h1>

      <div className="card">
        <input
          placeholder="Receiver Email"
          value={receiver}
          onChange={(e) => setReceiver(e.target.value)}
        />
        <input
          type="number"
          placeholder="Amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
        <input
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <button onClick={sendMoney}>Send</button>
      </div>

      <button onClick={downloadStatement}>Download Statement</button>

      {history.map((tx) => (
        <div key={tx.transactionId} className="card small">
          ₹{tx.amount} - {tx.description}
        </div>
      ))}
    </div>
  );
}