const API_URL = 'http://127.0.0.1:5000';

const loginForm    = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const mensaje      = document.getElementById('mensaje');
const toggleLink   = document.getElementById('toggle-link');
const toggleText   = document.getElementById('toggle-text');

function mostrarMensaje(texto, tipo = 'error') {
  mensaje.textContent = texto;
  mensaje.className = 'mensaje ' + tipo; // "mensaje error" o "mensaje exito"
}

function limpiarMensaje() {
  mensaje.textContent = '';
  mensaje.className = 'mensaje';
}

toggleLink.addEventListener('click', (e) => {
  e.preventDefault(); // evita que el <a href="#"> salte al inicio de la página

  const loginVisible = !loginForm.classList.contains('hidden');

  if (loginVisible) {
    // Estamos en login -> pasar a registro
    loginForm.classList.add('hidden');
    registerForm.classList.remove('hidden');
    toggleText.textContent = '¿Ya tienes cuenta?';
    toggleLink.textContent = 'Inicia sesión';
  } else {
    // Estamos en registro -> volver a login
    registerForm.classList.add('hidden');
    loginForm.classList.remove('hidden');
    toggleText.textContent = '¿No tienes cuenta?';
    toggleLink.textContent = 'Regístrate';
  }
  limpiarMensaje();
});

loginForm.addEventListener('submit', async (e) => {
  e.preventDefault(); // CRÍTICO: evita que el form recargue la página
  limpiarMensaje();

  const email    = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;

  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (!response.ok) {
      // 400, 401, etc.
      mostrarMensaje(data.error || 'Error al iniciar sesión');
      return;
    }

    // Tu backend devuelve { "token": "..." }
    localStorage.setItem('token', data.token);
    mostrarMensaje('Login correcto, redirigiendo...', 'exito');

    // Redirigir al dashboard (aún no existe, pero lo crearemos)
    setTimeout(() => {
      window.location.href = 'dashboard.html';
    }, 500);

  } catch (err) {
    // Errores de red (backend caído, CORS, etc.)
    mostrarMensaje('No se pudo conectar con el servidor');
    console.error(err);
  }
});

registerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  limpiarMensaje();

  const name     = document.getElementById('register-name').value.trim();
  const username = document.getElementById('register-username').value.trim();
  const email    = document.getElementById('register-email').value.trim();
  const password = document.getElementById('register-password').value;

  if (!name || !username || !email || !password) {
    mostrarMensaje('Todos los campos son obligatorios');
    return;
  }

  try {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, username, email, password })
    });

    const data = await response.json();

    if (!response.ok) {
      // 400 (faltan datos), 409 (email/username ya existe)
      mostrarMensaje(data.error || 'Error al registrarse');
      return;
    }

    // Tu backend devuelve { "status": "El usuario X ... Se creó Correctamente" }
    mostrarMensaje(data.status || 'Cuenta creada correctamente', 'exito');

    // Limpiar form y volver al login tras 1.5s
    registerForm.reset();
    setTimeout(() => {
      registerForm.classList.add('hidden');
      loginForm.classList.remove('hidden');
      toggleText.textContent = '¿No tienes cuenta?';
      toggleLink.textContent = 'Regístrate';
      limpiarMensaje();
    }, 1500);

  } catch (err) {
    mostrarMensaje('No se pudo conectar con el servidor');
    console.error(err);
  }
});