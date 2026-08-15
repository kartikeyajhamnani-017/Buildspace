import React, { useEffect, useState } from "react";
import api from "../api/axiosConfig";

export default function DashboardHome() {
  const [balance, setBalance] = useState(0);

  useEffect(() => {
    api.get("/wallet/balance").then((res) => {
      setBalance(res.data.balance);
    });
  }, []);

  return (
    <div>
      <h1>Overview</h1>
      <div className="card">
        <h2>Total Balance</h2>
        <p>₹ {balance}</p>
      </div>
    </div>
  );
}