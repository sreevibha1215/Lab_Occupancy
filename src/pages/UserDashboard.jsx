import React, { useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import "../App.css";

function UserDashboard() {
  const navigate = useNavigate();

  // Disable scrolling when this component mounts
  useEffect(() => {
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "auto"; // re-enable when leaving
    };
  }, []);

  return (
    <div
      className="user-dashboard-container"
      style={{
        height: "100vh", // full screen height
        overflow: "hidden", // prevent scroll
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "linear-gradient(135deg, #a78bfa, #c084fc, #f0abfc)",
        backgroundSize: "400% 400%",
        animation: "gradientShift 10s ease infinite",
        fontFamily: "'Poppins', sans-serif",
        margin: 0,
        padding: 0,
      }}
    >
      <motion.div
        className="user-card"
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        whileHover={{ scale: 1.03 }}
        style={{
          backdropFilter: "blur(15px)",
          background: "rgba(255, 255, 255, 0.3)",
          border: "1px solid rgba(255, 255, 255, 0.4)",
          padding: "3rem 2.5rem",
          borderRadius: "25px",
          boxShadow: "0 10px 40px rgba(0,0,0,0.15)",
          textAlign: "center",
          width: "90%",
          maxWidth: "480px",
        }}
      >
        <motion.h1
          style={{
            color: "#4c1d95",
            fontWeight: "700",
            fontSize: "2.2rem",
            marginBottom: "1rem",
            fontFamily: "'Quicksand', sans-serif",
            letterSpacing: "1px",
          }}
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          Welcome, Explorer 🌟
        </motion.h1>

        <motion.p
          style={{
            color: "#312e81",
            fontSize: "1.05rem",
            marginBottom: "2rem",
            lineHeight: "1.6",
          }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          Dive into your personalized lab dashboard. Manage schedules, view
          availability, and make the most of your time efficiently.
        </motion.p>

        <motion.button
          onClick={() => navigate("/checklab")}
          whileHover={{
            scale: 1.08,
            boxShadow: "0 0 25px #a78bfa",
          }}
          whileTap={{ scale: 0.95 }}
          style={{
            background:
              "linear-gradient(90deg, #6d28d9, #8b5cf6, #c084fc, #e9d5ff)",
            backgroundSize: "300% 300%",
            animation: "gradientMove 5s ease infinite",
            border: "none",
            color: "white",
            padding: "0.9rem 2.2rem",
            borderRadius: "50px",
            fontSize: "1.1rem",
            fontWeight: "600",
            cursor: "pointer",
            transition: "all 0.4s ease",
            fontFamily: "'Poppins', sans-serif",
            letterSpacing: "0.5px",
          }}
        >
          🚀 Check Lab Availability
        </motion.button>

        <motion.div
          className="info-box"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          style={{
            marginTop: "2.5rem",
            backgroundColor: "rgba(245, 243, 255, 0.7)",
            borderRadius: "15px",
            padding: "1.2rem",
            fontSize: "1rem",
            color: "#4338ca",
            fontWeight: "500",
            boxShadow: "inset 0 0 15px rgba(255, 255, 255, 0.4)",
          }}
        >
          💡 <strong>Pro Tip:</strong> Stay updated with real-time lab
          availability — plan smarter and save time!
        </motion.div>
      </motion.div>

      <style>{`
        @keyframes gradientShift {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        @keyframes gradientMove {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
      `}</style>
    </div>
  );
}

export default UserDashboard;
