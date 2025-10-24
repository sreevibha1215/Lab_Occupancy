import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import "../AdminDashboard.css";

function AdminDashboard() {
  const [timetables, setTimetables] = useState([]);
  const [formData, setFormData] = useState({
    roomNumber: "",
    date: "",
    session: "",
    class: "",
    section: "",
    batch: "",
    subject: "",
    facultyName: "",
  });

  const [showForm, setShowForm] = useState(false);
  const [editIndex, setEditIndex] = useState(null);

  useEffect(() => {
    const mockData = [
      {
        roomNumber: "Lab-101",
        date: "2025-10-15",
        session: "Morning",
        class: "CSE",
        section: "A",
        batch: "2022",
        subject: "AI & ML",
        facultyName: "Dr. Ramesh",
      },
      {
        roomNumber: "Lab-102",
        date: "2025-10-16",
        session: "Afternoon",
        class: "ECE",
        section: "B",
        batch: "2023",
        subject: "VLSI",
        facultyName: "Dr. Kavitha",
      },
    ];
    setTimetables(mockData);
  }, []);

  const handleChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (editIndex !== null) {
      const updated = [...timetables];
      updated[editIndex] = formData;
      setTimetables(updated);
      setEditIndex(null);
    } else {
      setTimetables([...timetables, formData]);
    }
    setFormData({
      roomNumber: "",
      date: "",
      session: "",
      class: "",
      section: "",
      batch: "",
      subject: "",
      facultyName: "",
    });
    setShowForm(false);
    alert("✅ Timetable saved successfully!");
  };

  const handleEdit = (index) => {
    setFormData(timetables[index]);
    setEditIndex(index);
    setShowForm(true);
  };

  const handleDelete = (index) => {
    if (window.confirm("Are you sure you want to delete this timetable?")) {
      const updated = timetables.filter((_, i) => i !== index);
      setTimetables(updated);
    }
  };

  return (
    <div
      className="admin-bg"
      style={{
        backgroundImage:
          "url('https://images.unsplash.com/photo-1553877522-43269d4ea984?auto=format&fit=crop&w=1350&q=80')",
      }}
    >
      <div className="overlay"></div>

      <motion.div
        className="admin-container"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      >
        <motion.div
          className="admin-card glass"
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="dashboard-title">Admin Dashboard 🧠</h2>
          <p className="dashboard-subtitle">
            Manage and update all Lab Timetables efficiently
          </p>

          <div className="timetable-section">
            <h3 className="section-title">📅 Existing Timetables</h3>
            {timetables.length === 0 ? (
              <p className="no-data">No timetables available.</p>
            ) : (
              <motion.table
                className="timetable-table"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.5 }}
              >
                <thead>
                  <tr>
                    <th>Room</th>
                    <th>Date</th>
                    <th>Session</th>
                    <th>Class</th>
                    <th>Section</th>
                    <th>Batch</th>
                    <th>Subject</th>
                    <th>Faculty</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {timetables.map((item, index) => (
                    <motion.tr
                      key={index}
                      whileHover={{
                        scale: 1.02,
                        backgroundColor: "rgba(147, 51, 234, 0.08)",
                      }}
                    >
                      <td>{item.roomNumber}</td>
                      <td>{item.date}</td>
                      <td>{item.session}</td>
                      <td>{item.class}</td>
                      <td>{item.section}</td>
                      <td>{item.batch}</td>
                      <td>{item.subject}</td>
                      <td>{item.facultyName}</td>
                      <td>
                        <button
                          className="edit-btn"
                          onClick={() => handleEdit(index)}
                        >
                          Edit
                        </button>
                        <button
                          className="delete-btn"
                          onClick={() => handleDelete(index)}
                        >
                          Delete
                        </button>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </motion.table>
            )}
          </div>

          <div className="button-center">
            {!showForm && (
              <motion.button
                className="add-btn"
                onClick={() => {
                  setShowForm(true);
                  setEditIndex(null);
                }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                ➕ Add New Timetable
              </motion.button>
            )}
          </div>

          <AnimatePresence>
            {showForm && (
              <motion.div
                className="form-container glass-light"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -30 }}
                transition={{ duration: 0.5 }}
              >
                <h3 className="form-title">
                  {editIndex !== null ? "Edit Timetable ✏️" : "Add New Timetable 🧾"}
                </h3>
                <form onSubmit={handleSubmit} className="form-grid">
                  {Object.keys(formData).map((key) => (
                    <input
                      key={key}
                      type="text"
                      name={key}
                      placeholder={
                        key.charAt(0).toUpperCase() +
                        key.slice(1).replace(/([A-Z])/g, " $1")
                      }
                      value={formData[key]}
                      onChange={handleChange}
                      required
                    />
                  ))}
                  <div className="form-buttons">
                    <button type="submit" className="save-btn">
                      {editIndex !== null ? "Update" : "Save"}
                    </button>
                    <button
                      type="button"
                      className="cancel-btn"
                      onClick={() => setShowForm(false)}
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </motion.div>
    </div>
  );
}

export default AdminDashboard;
