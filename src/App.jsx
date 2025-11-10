// App.jsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import AdminDashboard from "./pages/AdminDashboard";
import UserDashboard from "./pages/UserDashboard";
import CheckLab from "./pages/CheckLab";
import ReserveLab from "./pages/ReserveLab";
import MyReservations from "./pages/MyReservations";
import Navbar from "./components/Navbar";
import "./App.css";

function App() {
  return (
    <Router>
      <MainApp />
    </Router>
  );
}

function MainApp() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/user" element={<UserDashboard />} />
        <Route path="/checklab" element={<CheckLab />} />
        <Route path="/reservelab" element={<ReserveLab />} />
        <Route path="/myreservations" element={<MyReservations />} />
      </Routes>
    </>
  );
}

export default App;
