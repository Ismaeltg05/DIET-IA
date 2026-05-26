/*
Autor: Ismael Torres González y Francisco J. Salmerón Puig
Comentador: Ismael Torres González y Francisco J. Salmerón Puig
*/

const express = require("express");
const router = express.Router();

/**
 * Rutas de autenticación.
 * - POST /auth/register: crea un nuevo usuario con email y contraseña.
 * - POST /auth/login: valida credenciales y devuelve el userId.
 */
const {
  register,
  login
} = require("../controllers/authController");

router.post("/register", register);
router.post("/login", login);

module.exports = router;