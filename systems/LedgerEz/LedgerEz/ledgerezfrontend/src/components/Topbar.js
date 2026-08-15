import React, { useContext } from "react";
import { AuthContext } from "../context/AuthContext";

export default function Topbar() {
  const { auth, logout } = useContext(AuthContext);

  return (
    <div className="topbar">
      <h1>Welcome {auth?.user?.sub || "User"}</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
}