const mongoose = require("mongoose");
const validator = require('validator');

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true
  },

  email: {
    type: String,
    required: true,
    unique: true,
    validate: {
      validator: (v) => validator.isEmail(v),
      message: 'El email no es válido'
    }
    //match: [/^[^\s@]+@[^\s@]+\.[^\s@]+$/, 'Email no válido']
  },

  password: {
    type: String,
    required: true
  },

  phone: {
    type: String,
    unique: true,
    sparse: true,
    trim: true,
    validate: {
      validator: (v) => validator.isMobilePhone(v, 'any'),
      message: 'El número de teléfono no es válido'
    }
  }

}, {
  timestamps: true
});

module.exports = mongoose.model("User", userSchema);