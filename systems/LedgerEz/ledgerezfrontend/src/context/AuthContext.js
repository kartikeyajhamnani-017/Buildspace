import React, { createContext, useState, useEffect, useContext } from "react";
import { jwtDecode } from "jwt-decode";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState(null);

  // Load token on first render
  useEffect(() => {
    const storedToken = localStorage.getItem("token");

    if (storedToken) {
      try {
        const decoded = jwtDecode(storedToken);
        setAuth({ token: storedToken, user: decoded });
      } catch (error) {
        console.error("Invalid token");
        localStorage.removeItem("token");
        setAuth(null);
      }
    }
  }, []);

  const login = (token) => {
    localStorage.setItem("token", token);
    const decoded = jwtDecode(token);
    setAuth({ token, user: decoded });
  };

  const logout = () => {
    localStorage.removeItem("token");
    setAuth(null);
  };

  return (
    <AuthContext.Provider
      value={{
        auth,
        token: auth?.token || null,
        user: auth?.user || null,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook (THIS WAS MISSING)
export const useAuth = () => {
  return useContext(AuthContext);
};