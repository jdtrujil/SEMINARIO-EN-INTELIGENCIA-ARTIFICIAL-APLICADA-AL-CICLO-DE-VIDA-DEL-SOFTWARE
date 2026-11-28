// Mejoras de la interfaz del taller. Todo funciona también sin JavaScript:
// estas funciones solo agregan ayudas en el navegador, nunca reglas de negocio.
"use strict";

(function () {
  var FORMATO_PLACA = /^[A-Z]{3}[0-9]{2}[A-Z]?$/;

  function pesos(valor) {
    return "$ " + Math.round(valor).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  }

  function entero(texto) {
    var limpio = (texto || "").trim().replace(/\.(?=\d{3}(\D|$))/g, "");
    return /^\d+$/.test(limpio) ? parseInt(limpio, 10) : null;
  }

  // Placa: mayúsculas mientras se escribe y aviso si el formato no sirve.
  document.querySelectorAll('input[name="placa"]').forEach(function (campo) {
    var ayuda = document.getElementById(campo.id + "-ayuda");
    function revisar() {
      var texto = campo.value.trim().toUpperCase();
      campo.classList.remove("valida", "invalida");
      if (!texto) { if (ayuda) ayuda.textContent = ""; return; }
      var ok = FORMATO_PLACA.test(texto);
      campo.classList.add(ok ? "valida" : "invalida");
      if (ayuda) ayuda.textContent = ok ? "Formato correcto" : "Use ABC12D o, si es antigua, ABC12";
    }
    campo.addEventListener("input", revisar);
    revisar();
  });

  // Lista del taller: filas que abren la orden, búsqueda y filtro por etapa.
  var filas = Array.prototype.slice.call(document.querySelectorAll(".lista tr[data-href]"));
  filas.forEach(function (fila) {
    fila.addEventListener("click", function (evento) {
      if (evento.target.tagName !== "A") window.location = fila.getAttribute("data-href");
    });
  });
  var buscador = document.getElementById("buscar");
  var etapaElegida = "";
  function filtrar() {
    var texto = buscador ? buscador.value.trim().toUpperCase() : "";
    filas.forEach(function (fila) {
      var coincide = !texto || fila.textContent.toUpperCase().indexOf(texto) !== -1;
      var etapaOk = !etapaElegida || fila.getAttribute("data-etapa") === etapaElegida;
      fila.hidden = !(coincide && etapaOk);
    });
  }
  if (buscador) buscador.addEventListener("input", filtrar);
  document.querySelectorAll("[data-filtro-etapa]").forEach(function (boton) {
    boton.addEventListener("click", function () {
      etapaElegida = boton.getAttribute("data-filtro-etapa");
      document.querySelectorAll("[data-filtro-etapa]").forEach(function (otro) {
        otro.classList.toggle("activo", otro === boton);
      });
      filtrar();
    });
  });

  // Copiar el número de orden para entregárselo al cliente.
  document.querySelectorAll("[data-copiar]").forEach(function (boton) {
    boton.hidden = false;
    boton.addEventListener("click", function () {
      var valor = boton.getAttribute("data-copiar");
      if (navigator.clipboard) {
        navigator.clipboard.writeText(valor).then(function () {
          boton.textContent = "Copiado";
          setTimeout(function () { boton.textContent = "Copiar número"; }, 1500);
        });
      }
    });
  });

  // Confirmar antes de una acción que no se puede deshacer.
  document.querySelectorAll("form[data-confirmar]").forEach(function (formulario) {
    formulario.addEventListener("submit", function (evento) {
      if (!window.confirm(formulario.getAttribute("data-confirmar"))) evento.preventDefault();
    });
  });

  // Subtotal en vivo mientras se escribe la cantidad y el precio.
  document.querySelectorAll("form[data-subtotal]").forEach(function (formulario) {
    var salida = formulario.querySelector(".subtotal-vivo");
    function calcular() {
      var cantidad = entero(formulario.elements.cantidad.value);
      var precio = entero(formulario.elements.precio.value);
      salida.textContent = cantidad && precio !== null ? "Subtotal: " + pesos(cantidad * precio) : "";
    }
    formulario.addEventListener("input", calcular);
    calcular();
  });

  // Imprimir la factura.
  document.querySelectorAll("[data-imprimir]").forEach(function (boton) {
    boton.hidden = false;
    boton.addEventListener("click", function () { window.print(); });
  });
})();
