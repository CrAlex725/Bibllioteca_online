from models import Usuario

# Usuario.es_admin()
def test_es_admin_true():
    user = Usuario()
    user.is_admin = True
    assert user.es_admin() is True

def test_es_admin_false():
    user = Usuario()
    user.is_admin = False
    assert user.es_admin() is False

# Usuario.set_password()
def test_set_password_hashea():
    user = Usuario()
    user.set_password("secreto123")
    assert user.password_hash != "secreto123"
    assert isinstance(user.password_hash, str)
    assert len(user.password_hash) > 20

# Usuario.perfil_completo()
# --- rut = None, phone = None ---
def test_perfil_rut_none_phone_none_address_none():
    user = Usuario()
    user.rut = None
    user.phone = None
    user.address = None
    assert user.perfil_completo() is False

def test_perfil_rut_none_phone_none_address_vacio():
    user = Usuario()
    user.rut = None
    user.phone = None
    user.address = ""
    assert user.perfil_completo() is False

def test_perfil_rut_none_phone_none_address_espacios():
    user = Usuario()
    user.rut = None
    user.phone = None
    user.address = "      "
    assert user.perfil_completo() is False

def test_perfil_rut_none_phone_none_address_completo():
    user = Usuario()
    user.rut = None
    user.phone = None
    user.address = "Calle 123"
    assert user.perfil_completo() is False

# --- rut = None, phone = "" ---
def test_perfil_rut_none_phone_vacio_address_none():
    user = Usuario()
    user.rut = None
    user.phone = ""
    user.address = None
    assert user.perfil_completo() is False

def test_perfil_rut_none_phone_vacio_address_vacio():
    user = Usuario()
    user.rut = None
    user.phone = ""
    user.address = ""
    assert user.perfil_completo() is False

def test_perfil_rut_none_phone_vacio_address_espacios():
    user = Usuario()
    user.rut = None
    user.phone = ""
    user.address = "      "
    assert user.perfil_completo() is False

def test_perfil_rut_none_phone_vacio_address_completo():
    user = Usuario()
    user.rut = None
    user.phone = ""
    user.address = "Calle 123"
    assert user.perfil_completo() is False

# --- rut = None, phone = "      " ---
def test_perfil_rut_none_phone_espacios_address_none():
    user = Usuario()
    user.rut = None
    user.phone = "      "
    user.address = None
    assert user.perfil_completo() is False

def test_perfil_rut_none_phone_espacios_address_vacio():
    user = Usuario()
    user.rut = None
    user.phone = "      "
    user.address = ""
    assert user.perfil_completo() is False

def test_perfil_rut_none_phone_espacios_address_espacios():
    user = Usuario()
    user.rut = None
    user.phone = "      "
    user.address = "      "
    assert user.perfil_completo() is False

def test_perfil_rut_none_phone_espacios_address_completo():
    user = Usuario()
    user.rut = None
    user.phone = "      "
    user.address = "Calle 123"
    assert user.perfil_completo() is False

# --- rut = None, phone = completo ---
def test_perfil_rut_none_phone_completo_address_none():
    user = Usuario()
    user.rut = None
    user.phone = "+56912345678"
    user.address = None
    assert user.perfil_completo() is False

def test_perfil_rut_none_phone_completo_address_vacio():
    user = Usuario()
    user.rut = None
    user.phone = "+56912345678"
    user.address = ""
    assert user.perfil_completo() is False

def test_perfil_rut_none_phone_completo_address_espacios():
    user = Usuario()
    user.rut = None
    user.phone = "+56912345678"
    user.address = "      "
    assert user.perfil_completo() is False

def test_perfil_rut_none_phone_completo_address_completo():
    user = Usuario()
    user.rut = None
    user.phone = "+56912345678"
    user.address = "Calle 123"
    assert user.perfil_completo() is False
    
# --- rut = "", phone = None ---
def test_perfil_rut_vacio_phone_none_address_none():
    user = Usuario()
    user.rut = ""
    user.phone = None
    user.address = None
    assert user.perfil_completo() is False

def test_perfil_rut_vacio_phone_none_address_vacio():
    user = Usuario()
    user.rut = ""
    user.phone = None
    user.address = ""
    assert user.perfil_completo() is False

def test_perfil_rut_vacio_phone_none_address_espacios():
    user = Usuario()
    user.rut = ""
    user.phone = None
    user.address = "      "
    assert user.perfil_completo() is False

def test_perfil_rut_vacio_phone_none_address_completo():
    user = Usuario()
    user.rut = ""
    user.phone = None
    user.address = "Calle 123"
    assert user.perfil_completo() is False

# --- rut = "", phone = "" ---
def test_perfil_rut_vacio_phone_vacio_address_none():
    user = Usuario()
    user.rut = ""
    user.phone = ""
    user.address = None
    assert user.perfil_completo() is False

def test_perfil_rut_vacio_phone_vacio_address_vacio():
    user = Usuario()
    user.rut = ""
    user.phone = ""
    user.address = ""
    assert user.perfil_completo() is False

def test_perfil_rut_vacio_phone_vacio_address_espacios():
    user = Usuario()
    user.rut = ""
    user.phone = ""
    user.address = "      "
    assert user.perfil_completo() is False

def test_perfil_rut_vacio_phone_vacio_address_completo():
    user = Usuario()
    user.rut = ""
    user.phone = ""
    user.address = "Calle 123"
    assert user.perfil_completo() is False

# --- rut = "", phone = "      " ---
def test_perfil_rut_vacio_phone_espacios_address_none():
    user = Usuario()
    user.rut = ""
    user.phone = "      "
    user.address = None
    assert user.perfil_completo() is False

def test_perfil_rut_vacio_phone_espacios_address_vacio():
    user = Usuario()
    user.rut = ""
    user.phone = "      "
    user.address = ""
    assert user.perfil_completo() is False

def test_perfil_rut_vacio_phone_espacios_address_espacios():
    user = Usuario()
    user.rut = ""
    user.phone = "      "
    user.address = "      "
    assert user.perfil_completo() is False

def test_perfil_rut_vacio_phone_espacios_address_completo():
    user = Usuario()
    user.rut = ""
    user.phone = "      "
    user.address = "Calle 123"
    assert user.perfil_completo() is False

# --- rut = "", phone = completo ---
def test_perfil_rut_vacio_phone_completo_address_none():
    user = Usuario()
    user.rut = ""
    user.phone = "+56912345678"
    user.address = None
    assert user.perfil_completo() is False

def test_perfil_rut_vacio_phone_completo_address_vacio():
    user = Usuario()
    user.rut = ""
    user.phone = "+56912345678"
    user.address = ""
    assert user.perfil_completo() is False

def test_perfil_rut_vacio_phone_completo_address_espacios():
    user = Usuario()
    user.rut = ""
    user.phone = "+56912345678"
    user.address = "      "
    assert user.perfil_completo() is False

def test_perfil_rut_vacio_phone_completo_address_completo():
    user = Usuario()
    user.rut = ""
    user.phone = "+56912345678"
    user.address = "Calle 123"
    assert user.perfil_completo() is False
    
# --- rut = "      ", phone = None ---
def test_perfil_rut_espacios_phone_none_address_none():
    user = Usuario()
    user.rut = "      "
    user.phone = None
    user.address = None
    assert user.perfil_completo() is False

def test_perfil_rut_espacios_phone_none_address_vacio():
    user = Usuario()
    user.rut = "      "
    user.phone = None
    user.address = ""
    assert user.perfil_completo() is False

def test_perfil_rut_espacios_phone_none_address_espacios():
    user = Usuario()
    user.rut = "      "
    user.phone = None
    user.address = "      "
    assert user.perfil_completo() is False

def test_perfil_rut_espacios_phone_none_address_completo():
    user = Usuario()
    user.rut = "      "
    user.phone = None
    user.address = "Calle 123"
    assert user.perfil_completo() is False

# --- rut = "      ", phone = "" ---
def test_perfil_rut_espacios_phone_vacio_address_none():
    user = Usuario()
    user.rut = "      "
    user.phone = ""
    user.address = None
    assert user.perfil_completo() is False

def test_perfil_rut_espacios_phone_vacio_address_vacio():
    user = Usuario()
    user.rut = "      "
    user.phone = ""
    user.address = ""
    assert user.perfil_completo() is False

def test_perfil_rut_espacios_phone_vacio_address_espacios():
    user = Usuario()
    user.rut = "      "
    user.phone = ""
    user.address = "      "
    assert user.perfil_completo() is False

def test_perfil_rut_espacios_phone_vacio_address_completo():
    user = Usuario()
    user.rut = "      "
    user.phone = ""
    user.address = "Calle 123"
    assert user.perfil_completo() is False

# --- rut = "      ", phone = "      " ---
def test_perfil_rut_espacios_phone_espacios_address_none():
    user = Usuario()
    user.rut = "      "
    user.phone = "      "
    user.address = None
    assert user.perfil_completo() is False

def test_perfil_rut_espacios_phone_espacios_address_vacio():
    user = Usuario()
    user.rut = "      "
    user.phone = "      "
    user.address = ""
    assert user.perfil_completo() is False

def test_perfil_rut_espacios_phone_espacios_address_espacios():
    user = Usuario()
    user.rut = "      "
    user.phone = "      "
    user.address = "      "
    assert user.perfil_completo() is False

def test_perfil_rut_espacios_phone_espacios_address_completo():
    user = Usuario()
    user.rut = "      "
    user.phone = "      "
    user.address = "Calle 123"
    assert user.perfil_completo() is False

# --- rut = "      ", phone = completo ---
def test_perfil_rut_espacios_phone_completo_address_none():
    user = Usuario()
    user.rut = "      "
    user.phone = "+56912345678"
    user.address = None
    assert user.perfil_completo() is False

def test_perfil_rut_espacios_phone_completo_address_vacio():
    user = Usuario()
    user.rut = "      "
    user.phone = "+56912345678"
    user.address = ""
    assert user.perfil_completo() is False

def test_perfil_rut_espacios_phone_completo_address_espacios():
    user = Usuario()
    user.rut = "      "
    user.phone = "+56912345678"
    user.address = "      "
    assert user.perfil_completo() is False

def test_perfil_rut_espacios_phone_completo_address_completo():
    user = Usuario()
    user.rut = "      "
    user.phone = "+56912345678"
    user.address = "Calle 123"
    assert user.perfil_completo() is False
    
# --- rut = completo, phone = None ---
def test_perfil_rut_completo_phone_none_address_none():
    user = Usuario()
    user.rut = "19683003-k"
    user.phone = None
    user.address = None
    assert user.perfil_completo() is False

def test_perfil_rut_completo_phone_none_address_vacio():
    user = Usuario()
    user.rut = "19683003-k"
    user.phone = None
    user.address = ""
    assert user.perfil_completo() is False

def test_perfil_rut_completo_phone_none_address_espacios():
    user = Usuario()
    user.rut = "19683003-k"
    user.phone = None
    user.address = "      "
    assert user.perfil_completo() is False

def test_perfil_rut_completo_phone_none_address_completo():
    user = Usuario()
    user.rut = "19683003-k"
    user.phone = None
    user.address = "Calle 123"
    assert user.perfil_completo() is False

# --- rut = completo, phone = "" ---
def test_perfil_rut_completo_phone_vacio_address_none():
    user = Usuario()
    user.rut = "19683003-k"
    user.phone = ""
    user.address = None
    assert user.perfil_completo() is False

def test_perfil_rut_completo_phone_vacio_address_vacio():
    user = Usuario()
    user.rut = "19683003-k"
    user.phone = ""
    user.address = ""
    assert user.perfil_completo() is False

def test_perfil_rut_completo_phone_vacio_address_espacios():
    user = Usuario()
    user.rut = "19683003-k"
    user.phone = ""
    user.address = "      "
    assert user.perfil_completo() is False

def test_perfil_rut_completo_phone_vacio_address_completo():
    user = Usuario()
    user.rut = "19683003-k"
    user.phone = ""
    user.address = "Calle 123"
    assert user.perfil_completo() is False

# --- rut = completo, phone = "      " ---
def test_perfil_rut_completo_phone_espacios_address_none():
    user = Usuario()
    user.rut = "19683003-k"
    user.phone = "      "
    user.address = None
    assert user.perfil_completo() is False

def test_perfil_rut_completo_phone_espacios_address_vacio():
    user = Usuario()
    user.rut = "19683003-k"
    user.phone = "      "
    user.address = ""
    assert user.perfil_completo() is False

def test_perfil_rut_completo_phone_espacios_address_espacios():
    user = Usuario()
    user.rut = "19683003-k"
    user.phone = "      "
    user.address = "      "
    assert user.perfil_completo() is False

def test_perfil_rut_completo_phone_espacios_address_completo():
    user = Usuario()
    user.rut = "19683003-k"
    user.phone = "      "
    user.address = "Calle 123"
    assert user.perfil_completo() is False

# --- rut = completo, phone = completo ---
def test_perfil_rut_completo_phone_completo_address_none():
    user = Usuario()
    user.rut = "19683003-k"
    user.phone = "+56912345678"
    user.address = None
    assert user.perfil_completo() is False

def test_perfil_rut_completo_phone_completo_address_vacio():
    user = Usuario()
    user.rut = "19683003-k"
    user.phone = "+56912345678"
    user.address = ""
    assert user.perfil_completo() is False

def test_perfil_rut_completo_phone_completo_address_espacios():
    user = Usuario()
    user.rut = "19683003-k"
    user.phone = "+56912345678"
    user.address = "      "
    assert user.perfil_completo() is False

def test_perfil_completo():
    user = Usuario()
    user.rut = "19683003-k"
    user.phone = "+56912345678"
    user.address = "Calle 123"
    assert user.perfil_completo() is True
    


# Usuario.check_password()
def test_check_password_funciona():
    user = Usuario()
    user.set_password("secreto123")
    assert user.check_password("secreto123") is True

def test_check_password_no_funciona():
    user = Usuario()
    user.set_password("secreto123")
    assert user.check_password("otra_Contraseña") is False
    