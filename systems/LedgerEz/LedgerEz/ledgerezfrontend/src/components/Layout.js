import React from "react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

export default function Layout({ children }) {
  return (
    <div className="app-container">
      <Sidebar />
      <div className="main-section">
        <Topbar />
        <div className="content">{children}</div>
      </div>
    </div>
  );
}