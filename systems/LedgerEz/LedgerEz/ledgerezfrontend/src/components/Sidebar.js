import React from "react";
import { Link, useLocation } from "react-router-dom";
import { FaWallet, FaExchangeAlt, FaUsers, FaHome } from "react-icons/fa";

export default function Sidebar() {
  const location = useLocation();

  const navItems = [
    { path: "/dashboard", label: "Home", icon: <FaHome /> },
    { path: "/wallet", label: "Wallet", icon: <FaWallet /> },
    { path: "/contacts", label: "Contacts", icon: <FaUsers /> },
    { path: "/transactions", label: "Transactions", icon: <FaExchangeAlt /> },
  ];

  return (
    <div className="sidebar">
      <h2 className="logo">LedgerEz</h2>
      {navItems.map((item) => (
        <Link
          key={item.path}
          to={item.path}
          className={
            location.pathname === item.path
              ? "nav-item active"
              : "nav-item"
          }
        >
          {item.icon}
          <span>{item.label}</span>
        </Link>
      ))}
    </div>
  );
}