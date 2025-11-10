import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import "./ReserveLab.css";

const API_URL = "http://localhost:5000/api";

function ReserveLab() {
  const [labs, setLabs] = useState([]);
  const [formData, setFormData] = useState({
    lab_number: "",
    date: "",
    start_time: "",
    end_time: "",
    num_participants: "",
    purpose: "",
    description: "",
    user_email: "",
    user_name: "",
    urgency: "normal"
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [alternatives, setAlternatives] = useState(null);

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

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setAlternatives(null);

    try {
      const response = await axios.post(`${API_URL}/reserve-lab`, formData);
      
      if (response.data.success) {
        setResult({
          type: response.data.status === 'approved' ? 'success' : 'pending',
          message: response.data.message,
          reservation_id: response.data.reservation_id,
          priority_score: response.data.priority_score
        });

        // If pending, fetch alternatives
        if (response.data.status === 'pending') {
          const altResponse = await axios.post(`${API_URL}/suggest-alternatives`, {
            lab_number: formData.lab_number,
            date: formData.date,
            start_time: formData.start_time,
            end_time: formData.end_time,
            num_participants: formData.num_participants
          });
          setAlternatives(altResponse.data);
        }

        // Reset form
        setFormData({
          lab_number: "",
          date: "",
          start_time: "",
          end_time: "",
          num_participants: "",
          purpose: "",
          description: "",
          user_email: "",
          user_name: "",
          urgency: "normal"
        });
      }
    } catch (error) {
      const errorData = error.response?.data;
      
      // Handle rejection with detailed explanation
      if (errorData && errorData.rejected) {
        setResult({
          type: 'rejected',
          score: errorData.score,
          reason: errorData.reason,
          recommendations: errorData.recommendations,
          breakdown: errorData.breakdown,
          flags: errorData.flags,
          detailed_explanation: errorData.detailed_explanation,
          message: errorData.message
        });
        
        // Set alternatives if available
        if (errorData.alternatives) {
          setAlternatives(errorData.alternatives);
        }
      } else {
        setResult({
          type: 'error',
          message: errorData?.message || error.message || 'Failed to submit reservation'
        });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="reserve-container"
      style={{
        backgroundImage:
          "url('https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=1400&q=80')",
      }}
    >
      <div className="overlay"></div>

      <motion.div
        className="reserve-box"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <h2>Reserve a Lab</h2>
        <p className="subtitle">Submit your lab reservation request</p>

        <form onSubmit={handleSubmit}>
          {/* Lab Selection */}
          <motion.select
            name="lab_number"
            value={formData.lab_number}
            onChange={handleChange}
            whileFocus={{ scale: 1.02 }}
            required
          >
            <option value="">Select Lab</option>
            {labs.map((lab) => (
              <option key={lab.lab_number} value={lab.lab_number}>
                {lab.lab_number} - {lab.building} (Capacity: {lab.capacity})
              </option>
            ))}
          </motion.select>


          {/* Date */}
          <motion.input
            type="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
            whileFocus={{ scale: 1.02 }}
            required
            min={new Date().toISOString().split('T')[0]}
          />

          {/* Time Range */}
          <div className="time-range">
            <motion.input
              type="time"
              name="start_time"
              placeholder="Start Time"
              value={formData.start_time}
              onChange={handleChange}
              whileFocus={{ scale: 1.02 }}
              required
            />
            <span className="time-separator">to</span>
            <motion.input
              type="time"
              name="end_time"
              placeholder="End Time"
              value={formData.end_time}
              onChange={handleChange}
              whileFocus={{ scale: 1.02 }}
              required
            />
          </div>

          {/* Number of Participants */}
          <motion.input
            type="number"
            name="num_participants"
            placeholder="Number of Participants"
            value={formData.num_participants}
            onChange={handleChange}
            whileFocus={{ scale: 1.02 }}
            min="1"
            max="200"
            required
          />

          {/* Purpose */}
          <motion.select
            name="purpose"
            value={formData.purpose}
            onChange={handleChange}
            whileFocus={{ scale: 1.02 }}
            required
          >
            <option value="">Select Purpose</option>
            <option value="emergency">Emergency</option>
            <option value="exam">Exam / Assessment</option>
            <option value="event">Event / Competition</option>
            <option value="lecture">Lecture / Class</option>
            <option value="workshop">Workshop / Training</option>
            <option value="meeting">Meeting</option>
            <option value="practice">Practice Session</option>
            <option value="other">Other</option>
          </motion.select>

          {/* Urgency Level */}
          <motion.select
            name="urgency"
            value={formData.urgency}
            onChange={handleChange}
            whileFocus={{ scale: 1.02 }}
            required
          >
            <option value="">Select Urgency</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="normal">Normal</option>
            <option value="low">Low</option>
          </motion.select>

          {/* Description */}
          <motion.textarea
            name="description"
            placeholder="Describe the purpose of your reservation (be specific for better approval chances)"
            value={formData.description}
            onChange={handleChange}
            whileFocus={{ scale: 1.02 }}
            rows="2"
            required
          />

          {/* User Info */}
          <motion.input
            type="text"
            name="user_name"
            placeholder="Your Name"
            value={formData.user_name}
            onChange={handleChange}
            whileFocus={{ scale: 1.02 }}
            required
          />

          <motion.input
            type="email"
            name="user_email"
            placeholder="Your Email"
            value={formData.user_email}
            onChange={handleChange}
            whileFocus={{ scale: 1.02 }}
            required
          />

          <motion.button
            className="reserve-btn"
            type="submit"
            disabled={loading}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {loading ? "Submitting..." : "Submit Reservation"}
          </motion.button>
        </form>

        {/* Result Display */}
        <AnimatePresence>
          {result && (
            <motion.div
              className={`result-box ${result.type}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.4 }}
            >
              {result.type === 'success' && (
                <>
                  <h4>✅ Reservation Approved!</h4>
                  <p>{result.message}</p>
                  <p className="reservation-id">Reservation ID: #{result.reservation_id}</p>
                  <p className="priority-score">Priority Score: {result.priority_score}</p>
                </>
              )}
              
              {result.type === 'pending' && (
                <>
                  <h4>⏳ Reservation Pending</h4>
                  <p>{result.message}</p>
                  <p className="priority-score">Priority Score: {result.priority_score}</p>
                  
                  {alternatives && (
                    <div className="alternatives">
                      {alternatives.alternative_labs?.length > 0 && (
                        <div>
                          <h5>Alternative Labs Available:</h5>
                          <ul>
                            {alternatives.alternative_labs.map((alt, idx) => (
                              <li key={idx}>
                                {alt.lab_number} - {alt.building} Floor {alt.floor} (Capacity: {alt.capacity})
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {alternatives.alternative_times?.length > 0 && (
                        <div>
                          <h5>Alternative Time Slots:</h5>
                          <ul>
                            {alternatives.alternative_times.map((alt, idx) => (
                              <li key={idx}>
                                {alt.start_time} - {alt.end_time} ({alt.session})
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </>
              )}
              
              {result.type === 'rejected' && (
                <>
                  <h4>⚠️ Reservation Not Approved</h4>
                  <p className="rejection-reason"><strong>Reason:</strong> {result.reason}</p>
                  <p className="priority-score">Score: {result.score}/100 (Minimum required: 50)</p>
                  
                  {result.recommendations && (
                    <div className="recommendations">
                      <h5>💡 How to Improve:</h5>
                      <p>{result.recommendations}</p>
                    </div>
                  )}
                  
                  {result.detailed_explanation && (
                    <div className="score-breakdown">
                      <h5>📊 Score Breakdown:</h5>
                      <ul>
                        {result.detailed_explanation.capacity_issue && (
                          <li><strong>Capacity:</strong> {result.detailed_explanation.capacity_issue}</li>
                        )}
                        {result.detailed_explanation.authenticity_issue && (
                          <li><strong>Authenticity:</strong> {result.detailed_explanation.authenticity_issue}</li>
                        )}
                        {result.detailed_explanation.timing_issue && (
                          <li><strong>Timing:</strong> {result.detailed_explanation.timing_issue}</li>
                        )}
                      </ul>
                    </div>
                  )}
                  
                  {alternatives && (
                    <div className="alternatives">
                      <h5>🔄 Try These Alternatives:</h5>
                      
                      {alternatives.alternative_labs?.length > 0 && (
                        <div>
                          <h6>Available Labs (Same Time):</h6>
                          <ul>
                            {alternatives.alternative_labs.map((alt, idx) => (
                              <li key={idx}>
                                <strong>{alt.lab_number}</strong> - {alt.building} (Capacity: {alt.capacity})
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {alternatives.alternative_times?.length > 0 && (
                        <div>
                          <h6>Available Time Slots (Same Lab):</h6>
                          <ul>
                            {alternatives.alternative_times.map((alt, idx) => (
                              <li key={idx}>
                                {alt.start_time} - {alt.end_time} ({alt.session})
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </>
              )}
              
              {result.type === 'error' && (
                <>
                  <h4>❌ Submission Failed</h4>
                  <p>{result.message}</p>
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}

export default ReserveLab;

