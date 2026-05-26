/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

const mongoose = require("mongoose");
const validator = require('validator');

/**
 * Esquema de usuario básico.
 * - Incluye validaciones para email y teléfono mediante `validator`.
 * - `timestamps: true` añade `createdAt` y `updatedAt` automáticamente.
 */
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