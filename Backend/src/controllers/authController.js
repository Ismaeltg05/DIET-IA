const User = require("../models/User");
const bcrypt = require("bcryptjs");

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

exports.register = async (req, res) => {
  try {
    const { name, email, password, phone } = req.body;

    if (!name || !email || !password) {
      return res.status(400).json({
        error: "Faltan campos obligatorios"
      });
    }

    if (!emailRegex.test(email)) {
      return res.status(400).json({
        error: "Email no válido"
      });
    }

    const existingUser = await User.findOne({ email });

    if (existingUser) {
      return res.status(409).json({
        error: "El usuario ya existe"
      });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const user = await User.create({
      name,
      email,
      password: hashedPassword,
      phone
    });

    return res.status(201).json({
      message: "Usuario creado correctamente",
      userId: user._id
    });

  } catch (error) {
    return res.status(500).json({
      error: error.message
    });
  }
};

exports.login = async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!emailRegex.test(email)) {
      return res.status(400).json({
        error: "Email no válido"
      });
    }

    const user = await User.findOne({ email });

    if (!user) {
      return res.status(401).json({
        error: "Credenciales inválidas"
      });
    }

    const validPassword = await bcrypt.compare(password, user.password);

    if (!validPassword) {
      return res.status(401).json({
        error: "Credenciales inválidas"
      });
    }

    return res.json({
      message: "Login correcto",
      userId: user._id
    });

  } catch (error) {
    return res.status(500).json({
      error: error.message
    });
  }
};