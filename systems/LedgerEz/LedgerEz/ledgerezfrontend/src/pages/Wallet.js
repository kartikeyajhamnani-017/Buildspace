import React, { useState, useEffect } from "react";
import api from "../api/axiosConfig";

export default function Wallet() {
  const [amount, setAmount] = useState("");
  const [balance, setBalance] = useState(0);

  const fetchBalance = () => {
    api.get("/wallet/balance").then((res) => {
      setBalance(res.data.balance);
    });
  };

  useEffect(fetchBalance, []);

  const addFunds = async () => {
    await api.post("/wallet/add", { amount });
    fetchBalance();
    setAmount("");
  };

  return (
    <div>
      <h1>Wallet</h1>
      <div className="card">
        <h3>Current Balance: ₹ {balance}</h3>
        <input
          type="number"
          placeholder="Enter amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
        <button onClick={addFunds}>Add Funds</button>
      </div>
    </div>
  );
}