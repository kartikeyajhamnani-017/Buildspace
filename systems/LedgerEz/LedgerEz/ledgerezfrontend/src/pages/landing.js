import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useEffect } from "react";

function Landing() {
  const navigate = useNavigate();
  const { token } = useAuth();

  useEffect(() => {
    if (token) {
      navigate("/dashboard");
    }
  }, [token, navigate]);

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>LedgerEz</h1>
        <p style={styles.subtitle}>
          Secure Digital Ledger Management
        </p>

        <button style={styles.primaryBtn} onClick={() => navigate("/login")}>
          Login
        </button>

        <button style={styles.secondaryBtn} onClick={() => navigate("/register")}>
          Register
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "#f4f6f9"
  },
  card: {
    background: "white",
    padding: "40px",
    borderRadius: "12px",
    boxShadow: "0 8px 24px rgba(0,0,0,0.1)",
    textAlign: "center",
    width: "350px"
  },
  title: {
    marginBottom: "10px"
  },
  subtitle: {
    marginBottom: "30px",
    color: "#555"
  },
  primaryBtn: {
    width: "100%",
    padding: "12px",
    marginBottom: "10px",
    background: "#2c3e50",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer"
  },
  secondaryBtn: {
    width: "100%",
    padding: "12px",
    marginBottom: "10px",
    background: "#2c3e50",
    color: "white",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer"
  }
};

export default Landing;