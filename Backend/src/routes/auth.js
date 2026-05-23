/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

const express = require("express");
const router = express.Router();

const {
  register,
  login
} = require("../controllers/authController");

router.post("/register", register);
router.post("/login", login);

module.exports = router;