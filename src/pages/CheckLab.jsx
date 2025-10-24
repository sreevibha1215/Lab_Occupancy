import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import "../App.css";
import "./CheckLab.css";

function CheckLab() {
  const [date, setDate] = useState("");
  const [session, setSession] = useState("");
  const [roomNumber, setRoomNumber] = useState("");
  const [result, setResult] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();

    if (roomNumber.toUpperCase() === "E401" && session === "morning") {
      setResult(
        "E401 is occupied by CSDS-A for Operating Systems with Dr. Madhuri 💻"
      );
    } else if (!roomNumber || !date || !session) {
      setResult("Please fill all fields to check lab status.");
    } else {
      setResult("✨ Yes, this lab is free!");
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
          <motion.input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            whileFocus={{ scale: 1.05 }}
            transition={{ duration: 0.3 }}
            required
          />

          <motion.select
            value={session}
            onChange={(e) => setSession(e.target.value)}
            whileFocus={{ scale: 1.05 }}
            transition={{ duration: 0.3 }}
            required
          >
            <option value="">Select Session</option>
            <option value="morning">
              Morning
            </option>
            <option value="afternoon">Afternoon</option>
          </motion.select>

          <motion.input
            type="text"
            placeholder="Enter Room Number (e.g., E401)"
            value={roomNumber}
            onChange={(e) => setRoomNumber(e.target.value)}
            whileFocus={{ scale: 1.05 }}
            transition={{ duration: 0.3 }}
            required
          />

          <motion.button
            className="check-btn"
            type="submit"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Check Availability
          </motion.button>
        </form>

        <AnimatePresence>
          {result && (
            <motion.div
              className="result-box"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.4 }}
            >
              {result}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}

export default CheckLab;
