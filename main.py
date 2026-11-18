# ============================================================
# SOFTWARE FJ - Sistema Integral de Gestión de Clientes,
# Servicios y Reservas
# POO: Abstracción, Herencia, Polimorfismo, Encapsulación
# Manejo Avanzado de Excepciones + Logs
# Sin Base de Datos - Solo Listas y Objetos
# ============================================================

from abc import ABC, abstractmethod
from datetime import datetime
import traceback

# ------------------------------------------------------------
# 1. SISTEMA DE LOGS
# ------------------------------------------------------------
def registrar_log(mensaje, nivel="INFO"):
    """Registra eventos y errores en errores.log sin detener el programa."""
    try:
        with open("errores.log", "a", encoding="utf-8") as archivo:
            hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            archivo.write(f"[{hora}] [{nivel}] {mensaje}\n")
    except Exception as e:
        print(f"No se pudo escribir log: {e}")

# ------------------------------------------------------------
# 2. EXCEPCIONES PERSONALIZADAS
# ------------------------------------------------------------
class ErrorSoftwareFJ(Exception):
    """Excepción base del sistema."""
    pass

class DatosInvalidosError(ErrorSoftwareFJ):
    pass

class ClienteInvalidoError(DatosInvalidosError):
    pass

class ServicioNoDisponibleError(ErrorSoftwareFJ):
    pass

class ReservaInvalidaError(ErrorSoftwareFJ):
    pass

class ParametroFaltanteError(ErrorSoftwareFJ):
    pass

# ------------------------------------------------------------
# 3. CLASE ABSTRACTA BASE - ENTIDAD
# ------------------------------------------------------------
class Entidad(ABC):
    def __init__(self, id_entidad, nombre):
        self._id = id_entidad
        self._nombre = nombre
        self._fecha_creacion = datetime.now()

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @abstractmethod
    def mostrar_info(self):
        pass

    def __str__(self):
        return f"[{self._id}] {self._nombre}"

# ------------------------------------------------------------
# 4. CLASE CLIENTE - ENCAPSULACIÓN + VALIDACIÓN
# ------------------------------------------------------------
class Cliente(Entidad):
    def __init__(self, id_cliente, nombre, email, telefono, edad):
        # Validaciones estrictas antes de crear
        if not nombre or not isinstance(nombre, str):
            raise ClienteInvalidoError("El nombre del cliente es obligatorio.")
        if "@" not in str(email) or "." not in str(email):
            raise ClienteInvalidoError(f"Email inválido: {email}")
        if not str(telefono).isdigit() or len(str(telefono)) < 7:
            raise ClienteInvalidoError(f"Teléfono inválido: {telefono}")
        if not isinstance(edad, int) or edad < 18:
            raise ClienteInvalidoError(f"Cliente debe ser mayor de edad. Edad recibida: {edad}")

        super().__init__(id_cliente, nombre)
        self.__email = email        # Privado - Encapsulación
        self.__telefono = telefono  # Privado
        self.__edad = edad          # Privado

    @property
    def email(self):
        return self.__email

    @property
    def telefono(self):
        return self.__telefono

    def mostrar_info(self):
        return f"Cliente {self._id} | {self._nombre} | {self.__email} | Tel: {self.__telefono} | Edad: {self.__edad}"

# ------------------------------------------------------------
# 5. CLASE ABSTRACTA SERVICIO
# ------------------------------------------------------------
class Servicio(Entidad):
    def __init__(self, id_servicio, nombre, precio_base, disponible=True):
        if precio_base is None:
            raise ParametroFaltanteError("Falta el precio_base del servicio.")
        if precio_base <= 0:
            raise DatosInvalidosError("El precio debe ser mayor a 0.")
        super().__init__(id_servicio, nombre)
        self._precio_base = precio_base
        self._disponible = disponible

    @property
    def disponible(self):
        return self._disponible

    @abstractmethod
    def calcular_costo(self, *args, **kwargs):
        """Método polimórfico - cada servicio calcula diferente."""
        pass

    @abstractmethod
    def describir(self):
        pass

    # MÉTODO SOBRECARGADO SIMULADO: mismo nombre, diferentes parámetros
    def calcular_costo_con_impuesto(self, duracion=1, descuento=0, impuesto=0.19):
        """Versión 1: con impuesto y descuento opcionales."""
        base = self.calcular_costo(duracion)
        total = base * (1 - descuento) * (1 + impuesto)
        return round(total, 2)

    def mostrar_info(self):
        return f"Servicio {self._id} | {self._nombre} | ${self._precio_base} | Disponible: {self._disponible}"

# ------------------------------------------------------------
# 6. TRES SERVICIOS ESPECIALIZADOS - HERENCIA + POLIMORFISMO
# ------------------------------------------------------------
class ReservaSala(Servicio):
    def __init__(self, id_servicio, nombre, precio_base, capacidad, disponible=True):
        super().__init__(id_servicio, nombre, precio_base, disponible)
        if capacidad <= 0:
            raise DatosInvalidosError("La capacidad de la sala debe ser > 0.")
        self._capacidad = capacidad

    def calcular_costo(self, duracion=1, **kwargs):
        if duracion <= 0:
            raise DatosInvalidosError("La duración debe ser mayor a 0.")
        return self._precio_base * duracion

    def describir(self):
        return f"Sala '{self._nombre}' - Capacidad {self._capacidad} personas - ${self._precio_base}/hora"

class AlquilerEquipo(Servicio):
    def __init__(self, id_servicio, nombre, precio_base, cantidad_stock, disponible=True):
        super().__init__(id_servicio, nombre, precio_base, disponible)
        if cantidad_stock < 0:
            raise DatosInvalidosError("El stock no puede ser negativo.")
        self._stock = cantidad_stock

    def calcular_costo(self, duracion=1, cantidad=1, **kwargs):
        if cantidad > self._stock:
            raise ServicioNoDisponibleError(f"Stock insuficiente. Pedido: {cantidad}, Disponible: {self._stock}")
        if duracion <= 0 or cantidad <= 0:
            raise DatosInvalidosError("Duración y cantidad deben ser > 0.")
        return self._precio_base * duracion * cantidad

    def describir(self):
        return f"Equipo '{self._nombre}' - Stock: {self._stock} - ${self._precio_base}/día por unidad"

class AsesoriaEspecializada(Servicio):
    def __init__(self, id_servicio, nombre, precio_base, nivel, disponible=True):
        super().__init__(id_servicio, nombre, precio_base, disponible)
        if nivel not in ["Básico", "Intermedio", "Avanzado"]:
            raise DatosInvalidosError("Nivel debe ser Básico, Intermedio o Avanzado.")
        self._nivel = nivel

    def calcular_costo(self, duracion=1, **kwargs):
        multiplicador = {"Básico": 1.0, "Intermedio": 1.5, "Avanzado": 2.0}[self._nivel]
        if duracion <= 0:
            raise DatosInvalidosError("Duración inválida.")
        return self._precio_base * duracion * multiplicador

    def describir(self):
        return f"Asesoría '{self._nombre}' - Nivel {self._nivel} - ${self._precio_base}/hora base"

# ------------------------------------------------------------
# 7. CLASE RESERVA
# ------------------------------------------------------------
class Reserva:
    _contador = 0

    def __init__(self, cliente, servicio, duracion, cantidad=1):
        if cliente is None or servicio is None:
            raise ParametroFaltanteError("Reserva requiere cliente y servicio.")
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("Cliente inválido para reserva.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"Servicio '{servicio.nombre}' no disponible.")
        if duracion <= 0:
            raise ReservaInvalidaError("Duración debe ser > 0.")

        Reserva._contador += 1
        self.id = Reserva._contador
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.cantidad = cantidad
        self.estado = "Pendiente"
        self.costo_total = 0

    def confirmar(self):
        try:
            # Encadenamiento de excepciones con 'raise ... from'
            try:
                self.costo_total = self.servicio.calcular_costo(self.duracion, cantidad=self.cantidad)
            except ServicioNoDisponibleError as e:
                raise ReservaInvalidaError(f"No se pudo confirmar reserva {self.id}") from e

            self.estado = "Confirmada"
            registrar_log(f"Reserva {self.id} confirmada - Cliente: {self.cliente.nombre} - Costo: ${self.costo_total}")
            return f"✅ Reserva {self.id} CONFIRMADA - {self.servicio.nombre} - Total: ${self.costo_total}"

        except ReservaInvalidaError as e:
            registrar_log(f"Error confirmando reserva {self.id}: {e} | Causa: {e.__cause__}", "ERROR")
            self.estado = "Fallida"
            raise

    def cancelar(self):
        if self.estado == "Cancelada":
            raise ReservaInvalidaError(f"Reserva {self.id} ya estaba cancelada.")
        self.estado = "Cancelada"
        registrar_log(f"Reserva {self.id} cancelada.")
        return f"Reserva {self.id} cancelada."

    def __str__(self):
        return f"Reserva {self.id} | {self.cliente.nombre} | {self.servicio.nombre} | Estado: {self.estado} | Total: ${self.costo_total}

# ------------------------------------------------------------
# 8. SISTEMA PRINCIPAL - LISTAS INTERNAS
# ------------------------------------------------------------
class SistemaFJ:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def agregar_cliente(self, cliente):
        self.clientes.append(cliente)
        registrar_log(f"Cliente agregado: {cliente.nombre}")

    def agregar_servicio(self, servicio):
        self.servicios.append(servicio)
        registrar_log(f"Servicio agregado: {servicio.nombre}")

    def crear_reserva(self, cliente, servicio, duracion, cantidad=1):
        reserva = Reserva(cliente, servicio, duracion, cantidad)
        self.reservas.append(reserva)
        return reserva

    def listar_todo(self):
        print("\n--- CLIENTES ---")
        for c in self.clientes: print(c.mostrar_info())
        print("\n--- SERVICIOS (Polimorfismo) ---")
        for s in self.servicios: print(s.describir(), f"| Costo 2h: ${s.calcular_costo(2)}")
        print("\n--- RESERVAS ---")
        for r in self.reservas: print(r)

# ------------------------------------------------------------
# 9. SIMULACIÓN DE 10 OPERACIONES - CON try/except/else/finally
# ------------------------------------------------------------
def main():
    print("="*60)
    print("  SOFTWARE FJ - SISTEMA INTEGRAL")
    print("="*60)
    sistema = SistemaFJ()

    # OPERACIÓN 1: Cliente válido
    try:
        c1 = Cliente(1, "Ana Pérez", "ana@email.com", "3001234567", 25)
        sistema.agregar_cliente(c1)
        print("Op 1 OK: Cliente válido creado")
    except ClienteInvalidoError as e:
        registrar_log(f"Op 1 Error: {e}", "ERROR"); print(f"Op 1 FALLÓ: {e}")
    finally:
        print("Op 1 finalizada (finally)")

    # OPERACIÓN 2: Cliente inválido - email malo
    try:
        c_malo = Cliente(2, "Juan", "juan-sin-arroba", "123", 15)
        sistema.agregar_cliente(c_malo)
    except ClienteInvalidoError as e:
        registrar_log(f"Op 2 Error: {e}", "ERROR"); print(f"Op 2 FALLÓ (esperado): {e}")
    else:
        print("Op 2: Sin error inesperado")
    finally:
        print("Op 2 finalizada - sistema sigue vivo")

    # OPERACIÓN 3: Cliente válido 2
    try:
        c2 = Cliente(3, "Carlos Ruiz", "carlos@email.com", "3109876543", 30)
        sistema.agregar_cliente(c2)
        print("Op 3 OK: Segundo cliente creado")
    except Exception as e:
        registrar_log(f"Op 3: {e}", "ERROR")

    # OPERACIÓN 4: Servicios válidos (3 tipos)
    try:
        s1 = ReservaSala(101, "Sala A", 50000, capacidad=20)
        s2 = AlquilerEquipo(102, "Proyector 4K", 80000, cantidad_stock=5)
        s3 = AsesoriaEspecializada(103, "Asesoría Python", 120000, nivel="Avanzado")
        for s in [s1, s2, s3]: sistema.agregar_servicio(s)
        print("Op 4 OK: 3 servicios creados")
    except (DatosInvalidosError, ParametroFaltanteError) as e:
        registrar_log(f"Op 4: {e}", "ERROR"); print(f"Op 4 FALLÓ: {e}")

    # OPERACIÓN 5: Servicio inválido - precio negativo
    try:
        s_malo = ReservaSala(104, "Sala Mala", -1000, capacidad=10)
        sistema.agregar_servicio(s_malo)
    except DatosInvalidosError as e:
        registrar_log(f"Op 5: {e}", "ERROR"); print(f"Op 5 FALLÓ (esperado): {e}")

    # OPERACIÓN 6: Servicio inválido - parámetro faltante
    try:
        s_falta = AlquilerEquipo(105, "Laptop", None, cantidad_stock=2)
    except ParametroFaltanteError as e:
        registrar_log(f"Op 6: {e}", "ERROR"); print(f"Op 6 FALLÓ (esperado): {e}")

    # OPERACIÓN 7: Reserva exitosa
    try:
        r1 = sistema.crear_reserva(c1, s1, duracion=2)
        print(r1.confirmar())
        # Demostración método sobrecargado: con impuesto y descuento
        print(f"   Costo con impuesto y 10% descuento: ${s1.calcular_costo_con_impuesto(2, descuento=0.10)}")
    except Exception as e:
        registrar_log(f"Op 7: {e} - {traceback.format_exc()}", "ERROR"); print(f"Op 7 FALLÓ: {e}")
    else:
        print("Op 7 else: Reserva creada sin errores")

    # OPERACIÓN 8: Reserva fallida - servicio no disponible
    try:
        s_no_disp = ReservaSala(106, "Sala B", 60000, capacidad=10, disponible=False)
        sistema.agregar_servicio(s_no_disp)
        r_mala = sistema.crear_reserva(c1, s_no_disp, duracion=1)
        print(r_mala.confirmar())
    except ServicioNoDisponibleError as e:
        registrar_log(f"Op 8: {e}", "ERROR"); print(f"Op 8 FALLÓ (esperado): {e}")

    # OPERACIÓN 9: Reserva fallida - stock insuficiente + encadenamiento
    try:
        r2 = sistema.crear_reserva(c2, s2, duracion=1, cantidad=10)
        print(r2.confirmar())
    except ReservaInvalidaError as e:
        registrar_log(f"Op 9: {e} Causa: {e.__cause__}", "ERROR")
        print(f"Op 9 FALLÓ (esperado): {e} | Causa original: {e.__cause__}")

    # OPERACIÓN 10: Reserva exitosa + cancelación
    try:
        r3 = sistema.crear_reserva(c2, s3, duracion=3)
        print(r3.confirmar())
        print(r3.cancelar())
        # Intentar cancelar dos veces -> error controlado
        print(r3.cancelar())
    except ReservaInvalidaError as e:
        registrar_log(f"Op 10: {e}", "ERROR"); print(f"Op 10 FALLÓ controlado: {e}")
    finally:
        print("Op 10 finalizada")
    
    sistema.listar_todo()
    print("\n✅ SISTEMA TERMINO SIN CAERSE. Revisa errores.log")
    print("="*60)
    if __name__ == "__main__":
    main()
    


