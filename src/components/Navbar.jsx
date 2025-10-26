import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./Navbar.css";

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    navigate("/");
  };

  // Normalize path to prevent trailing slash mismatch
  const currentPath = location.pathname.replace(/\/$/, "");

  // ✅ Show Logout for Admin, CheckLab, ReserveLab, and MyReservations pages
  const showLogout = currentPath === "/admin" || currentPath === "/checklab" || currentPath === "/reservelab" || currentPath === "/myreservations";

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <div className="navbar-left">
          <img
            src="https://upload.wikimedia.org/wikipedia/en/e/e5/Official_logo_of_VNRVJIET.png"
            alt="VNRVJIET Logo"
            className="logo"
          />
          <div className="college-name">
            <h2>
              Vallurupalli Nageswara Rao Vignana Jyothi Institute of Engineering & Technology
            </h2>
          </div>
        </div>

        {showLogout && (
          <div className="navbar-right">
            <button className="logout-btn" onClick={handleLogout}>
<svg
  xmlns="http://www.w3.org/2000/svg"
  height="25px"
  width="25px"
  viewBox="0 -960 960 960"
  fill="#1f1f1f"
  style={{ padding: "3px", verticalAlign: "middle" }}
>
  <path d="M200-120q-33 0-56.5-23.5T120-200v-160h80v160h560v-560H200v160h-80v-160q0-33 23.5-56.5T200-840h560q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H200Zm220-160-56-58 102-102H120v-80h346L364-622l56-58 200 200-200 200Z"/>
</svg>
<span style={{ marginLeft: "6px", fontWeight: "600" }}>Logout</span>
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
