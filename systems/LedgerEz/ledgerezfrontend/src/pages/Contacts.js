import { useEffect, useState, useCallback } from "react";
import axios from "axios";
import { useAuth } from "../context/AuthContext";

function Contacts() {
  const { token } = useAuth();

  const [contacts, setContacts] = useState([]);
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");

  // Memoized fetch function
  const fetchContacts = useCallback(async () => {
    if (!token) return;

    try {
      const response = await axios.get(
        "http://localhost:9000/api/v1/contacts/getcontacts",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setContacts(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error(err);
      setContacts([]);
    }
  }, [token]);

  // Fetch contacts when token changes
  useEffect(() => {
    fetchContacts();
  }, [fetchContacts]);

  const handleAddContact = async (e) => {
    e.preventDefault();
    setError("");

    if (!email.trim()) return;

    try {
      await axios.post(
        "http://localhost:9000/api/v1/contacts/add",
        { email },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setEmail("");
      fetchContacts(); // Refresh list
    } catch (err) {
      console.error(err);
      setError("Unable to add contact. Check email or duplicate entry.");
    }
  };

  return (
    <div style={styles.container}>
      <h2>Your Contacts</h2>

      <form onSubmit={handleAddContact} style={styles.form}>
        <input
          type="email"
          placeholder="Enter contact email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={styles.input}
        />
        <button type="submit" style={styles.button}>
          Add
        </button>
      </form>

      {error && <p style={styles.error}>{error}</p>}

      {contacts.length === 0 ? (
        <p>No contacts added yet.</p>
      ) : (
        <div style={styles.list}>
          {contacts.map((contact) => (
            <div key={contact.contactId} style={styles.card}>
              <strong>{contact.contactName}</strong>
              <p>{contact.contactEmail}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: { padding: "20px" },
 form: {
  display: "flex",
  gap: "10px",
  marginBottom: "20px",
  alignItems: "center",
},

input: {
  padding: "14px 16px",
  flex: 3,                // 👈 takes more space
  borderRadius: "8px",
  border: "1px solid #ccc",
  fontSize: "16px",
},

button: {
  padding: "10px 16px",   // 👈 smaller padding
  flex: 1,                // 👈 takes less space
  borderRadius: "8px",
  border: "none",
  background: "#2c3e50",
  color: "white",
  cursor: "pointer",
  fontSize: "14px",
},
  list: { display: "flex", flexDirection: "column", gap: "10px" },
  card: {
    padding: "12px",
    borderRadius: "8px",
    background: "#f4f6f9",
  },
  error: { color: "red", marginBottom: "10px" },
};

export default Contacts;