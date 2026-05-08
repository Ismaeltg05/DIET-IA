const mongoose = require("mongoose");

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true
  },

  email: {
    type: String,
    required: true,
    unique: true,
    match: [/^[^\s@]+@[^\s@]+\.[^\s@]+$/, 'Email no válido']
  },

  password: {
    type: String,
    required: true
  },

  phone: {
    type: String,
    default: null
  }

}, {
  timestamps: true
});

module.exports = mongoose.model("User", userSchema);