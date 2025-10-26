import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import "../App.css";
import "./CheckLab.css";

const API_URL = "http://localhost:5000/api";

function CheckLab() {
  const [date, setDate] = useState("");
  const [session, setSession] = useState("");
  const [roomNumber, setRoomNumber] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [labs, setLabs] = useState([]);

  useEffect(() => {
    fetchLabs();
  }, []);

  const fetchLabs = async () => {
    try {
      const response = await axios.get(`${API_URL}/labs`);
      setLabs(response.data);
    } catch (error) {
      console.error("Error fetching labs:", error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post(`${API_URL}/check-availability`, {
        lab_number: roomNumber,
        date,
        session,
        start_time: startTime,
        end_time: endTime
      });

      if (response.data.available) {
        setResult({
          available: true,
          message: `✨ ${roomNumber} is available on ${date} during ${session} session!`
        });
      } else {
        const { reason, details } = response.data;
        
        if (reason === "occupied_by_class") {
          setResult({
            available: false,
            message: `❌ ${roomNumber} is occupied by ${details.class}-${details.section} for ${details.subject} with ${details.faculty_name}`
          });
        } else if (reason === "reserved") {
          setResult({
            available: false,
            message: `❌ ${roomNumber} is reserved for ${details.purpose} by ${details.reserved_by}`
          });
        }
      }
    } catch (error) {
      setResult({
        available: false,
        message: error.response?.data?.error || "Error checking availability. Please try again."
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="checklab-container"
      style={{
        backgroundImage:
          "url('https://images.shiksha.com/mediadata/images/1695814007phpkJ7At3.jpeg')",
      }}
    >
      <div className="overlay"></div>

      <motion.div
        className="checklab-box"
        initial={{ opacity: 0, y: -25 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <h2>Check Lab Availability</h2>
        <p className="subtitle">Find out if a lab is free for your session</p>

        <form onSubmit={handleSubmit}>
          <motion.select
            value={roomNumber}
            onChange={(e) => setRoomNumber(e.target.value)}
            whileFocus={{ scale: 1.05 }}
            transition={{ duration: 0.3 }}
            required
          >
            <option value="">Select Lab</option>
            {labs.map((lab) => (
              <option key={lab.lab_number} value={lab.lab_number}>
                {lab.lab_number} - {lab.building}
              </option>
            ))}
          </motion.select>

          <motion.input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            whileFocus={{ scale: 1.05 }}
            transition={{ duration: 0.3 }}
            required
            min={new Date().toISOString().split('T')[0]}
          />

          <motion.select
            value={session}
            onChange={(e) => setSession(e.target.value)}
            whileFocus={{ scale: 1.05 }}
            transition={{ duration: 0.3 }}
            required
          >
            <option value="">Select Session</option>
            <option value="morning">Morning</option>
            <option value="afternoon">Afternoon</option>
            <option value="evening">Evening</option>
          </motion.select>

          <div style={{ display: "flex", gap: "10px" }}>
            <motion.input
              type="time"
              placeholder="Start Time"
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              whileFocus={{ scale: 1.05 }}
              transition={{ duration: 0.3 }}
              style={{ flex: 1 }}
            />
            <motion.input
              type="time"
              placeholder="End Time"
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              whileFocus={{ scale: 1.05 }}
              transition={{ duration: 0.3 }}
              style={{ flex: 1 }}
            />
          </div>

          <motion.button
            className="check-btn"
            type="submit"
            disabled={loading}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {loading ? "Checking..." : "Check Availability"}
          </motion.button>
        </form>

        <AnimatePresence>
          {result && (
            <motion.div
              className={`result-box ${result.available ? 'available' : 'unavailable'}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.4 }}
            >
              {result.message}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}

export default CheckLab;
