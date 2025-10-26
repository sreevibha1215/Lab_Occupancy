import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import axios from "axios";
import "./MyReservations.css";

const API_URL = "http://localhost:5000/api";

function MyReservations() {
  const [reservations, setReservations] = useState([]);
  const [userEmail, setUserEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const fetchReservations = async () => {
    if (!userEmail) {
      setMessage({ type: "error", text: "Please enter your email" });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const response = await axios.get(`${API_URL}/reservations/${userEmail}`);
      setReservations(response.data);
      
      if (response.data.length === 0) {
        setMessage({ type: "info", text: "No reservations found for this email" });
      }
    } catch (error) {
      setMessage({ type: "error", text: "Error fetching reservations" });
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (reservationId) => {
    if (!window.confirm("Are you sure you want to cancel this reservation?")) {
      return;
    }

    try {
      await axios.delete(`${API_URL}/reservations/${reservationId}`);
      setMessage({ type: "success", text: "Reservation cancelled successfully" });
      fetchReservations(); // Refresh list
    } catch (error) {
      setMessage({ 
        type: "error", 
        text: error.response?.data?.error || "Error cancelling reservation" 
      });
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "approved": return "#10b981";
      case "pending": return "#f59e0b";
      case "rejected": return "#ef4444";
      case "cancelled": return "#6b7280";
      default: return "#6b7280";
    }
  };

  const getStatusEmoji = (status) => {
    switch (status) {
      case "approved": return "✅";
      case "pending": return "⏳";
      case "rejected": return "❌";
      case "cancelled": return "🚫";
      default: return "ℹ️";
    }
  };

  const canModify = (reservation) => {
    const reservationDate = new Date(`${reservation.date} ${reservation.start_time}`);
    const now = new Date();
    const hoursDiff = (reservationDate - now) / (1000 * 60 * 60);
    
    return hoursDiff >= 24 && reservation.status !== 'cancelled' && reservation.status !== 'rejected';
  };

  return (
    <div className="myreservations-container">
      <div className="overlay"></div>

      <motion.div
        className="myreservations-box"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <h3 style={{ marginBottom: "4px" }}>My Reservations</h3>
        <p className="subtitle">View and manage your lab reservations</p>

        <div className="email-search">
          <input
            type="email"
            placeholder="Enter your email"
            value={userEmail}
            onChange={(e) => setUserEmail(e.target.value)}
          />
          <button onClick={fetchReservations} disabled={loading}>
            {loading ? "Loading..." : "View My Reservations"}
          </button>
        </div>

        {message && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}

        {reservations.length > 0 && (
          <div className="reservations-list">
            {reservations.map((reservation) => (
              <motion.div
                key={reservation.id}
                className="reservation-card"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <div className="reservation-header">
                  <h3>{reservation.lab_number}</h3>
                  <span 
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(reservation.status) }}
                  >
                    {getStatusEmoji(reservation.status)} {reservation.status.toUpperCase()}
                  </span>
                </div>

                <div className="reservation-details">
                  <p><strong>Date:</strong> {reservation.date}</p>
                  <p><strong>Time:</strong> {reservation.start_time} - {reservation.end_time}</p>
                  <p><strong>Participants:</strong> {reservation.num_participants}</p>
                  <p><strong>Purpose:</strong> {reservation.purpose}</p>
                  <p><strong>Description:</strong> {reservation.description}</p>
                  <p><strong>Priority Score:</strong> {reservation.priority_score?.toFixed(1)}</p>
                  <p className="created-at"><strong>Requested:</strong> {new Date(reservation.created_at).toLocaleString()}</p>
                </div>

                {canModify(reservation) && (
                  <div className="reservation-actions">
                    <button 
                      className="cancel-btn"
                      onClick={() => handleCancel(reservation.id)}
                    >
                      Cancel Reservation
                    </button>
                  </div>
                )}

                {!canModify(reservation) && reservation.status !== 'cancelled' && reservation.status !== 'rejected' && (
                  <p className="modify-note">Cannot modify within 24 hours of reservation</p>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
}

export default MyReservations;

