"""
Base de conocimientos para el chatbot de MultiAndamios
Contiene información detallada sobre productos, servicios, precios, y políticas
"""

# Productos: Información detallada sobre los productos ofrecidos
PRODUCTOS = {
    "andamios": {
        "tipos": [
            {
                "nombre": "Andamios Multidireccionales",
                "descripcion": "Sistema modular de alta versatilidad para estructuras complejas y trabajos en altura que requieren múltiples niveles y configuraciones irregulares.",
                "especificaciones": "Carga máxima: 750kg/m², Altura máxima recomendada: 30 metros, Material: Acero galvanizado de alta resistencia",
                "usos": "Ideal para fachadas complejas, estructuras irregulares, rehabilitaciones y restauraciones",
                "precio_diario": 10000,
                "precio_semanal": 50000,
                "precio_mensual": 150000,
                "disponibilidad": "Alta - Más de 5000 m² en stock"
            },
            {
                "nombre": "Andamios de Marco",
                "descripcion": "Sistema tradicional de marcos y crucetas, fácil de montar y desmontar, perfecto para trabajos lineales.",
                "especificaciones": "Carga máxima: 500kg/m², Altura máxima recomendada: 20 metros, Material: Acero galvanizado",
                "usos": "Perfecto para fachadas regulares, trabajos lineales y proyectos residenciales",
                "precio_diario": 8000,
                "precio_semanal": 40000,
                "precio_mensual": 120000,
                "disponibilidad": "Alta - Más de 8000 m² en stock"
            },
            {
                "nombre": "Torres Móviles",
                "descripcion": "Estructuras ligeras y versátiles con ruedas bloqueables para fácil desplazamiento en obra.",
                "especificaciones": "Carga máxima: 300kg/plataforma, Altura máxima: 12 metros, Material: Aluminio ligero o acero",
                "usos": "Mantenimiento industrial, instalaciones eléctricas, trabajos de pintura y acabados",
                "precio_diario": 12000,
                "precio_semanal": 60000,
                "precio_mensual": 180000,
                "disponibilidad": "Media - 50 torres disponibles"
            },
            {
                "nombre": "Andamios Colgantes",
                "descripcion": "Sistemas suspendidos mediante cables, con mecanismos de elevación eléctricos o manuales.",
                "especificaciones": "Carga máxima: 400kg/plataforma, Longitud: hasta 8 metros, Material: Aluminio y acero",
                "usos": "Limpieza de ventanas, mantenimiento de fachadas y trabajos en altura sin acceso desde el suelo",
                "precio_diario": 15000,
                "precio_semanal": 75000,
                "precio_mensual": 225000,
                "disponibilidad": "Baja - Requiere reserva anticipada"
            }
        ],
        "accesorios": [
            {
                "nombre": "Escaleras integradas para andamios",
                "precio_semanal": 15000,
                "disponibilidad": "Alta"
            },
            {
                "nombre": "Barandillas de seguridad",
                "precio_semanal": 8000,
                "disponibilidad": "Alta"
            },
            {
                "nombre": "Rodapiés",
                "precio_semanal": 5000,
                "disponibilidad": "Alta"
            },
            {
                "nombre": "Viseras de protección",
                "precio_semanal": 12000,
                "disponibilidad": "Media"
            },
            {
                "nombre": "Redes de seguridad",
                "precio_semanal": 10000,
                "disponibilidad": "Alta"
            }
        ],
        "certificaciones": [
            "ISO 9001:2015 - Sistemas de Gestión de Calidad",
            "ISO 45001:2018 - Seguridad y Salud en el Trabajo",
            "Certificación CE para equipos de construcción",
            "Normativa OSHA de seguridad"
        ]
    },
    "formaletas": {
        "tipos": [
            {
                "nombre": "Formaletas para Columnas Circulares",
                "descripcion": "Moldes cilíndricos para columnas de concreto con acabado liso.",
                "especificaciones": "Diámetros disponibles: 20cm, 30cm, 40cm, 50cm, 60cm. Alturas modulares de 1 metro.",
                "usos": "Construcción de columnas circulares en edificaciones",
                "precio_diario": 8000,
                "precio_semanal": 40000,
                "precio_mensual": 120000,
                "disponibilidad": "Alta - Todas las medidas disponibles"
            },
            {
                "nombre": "Formaletas para Columnas Cuadradas",
                "descripcion": "Sistema modular para columnas cuadradas y rectangulares.",
                "especificaciones": "Dimensiones disponibles: desde 20x20cm hasta 60x60cm. Configurables en incrementos de 5cm.",
                "usos": "Columnas estructurales en edificaciones residenciales y comerciales",
                "precio_diario": 7500,
                "precio_semanal": 37500,
                "precio_mensual": 112500,
                "disponibilidad": "Alta"
            },
            {
                "nombre": "Formaletas para Muros",
                "descripcion": "Paneles modulares metálicos para vaciado de muros de concreto.",
                "especificaciones": "Paneles de 60x240cm, 90x240cm, y 120x240cm. Espesor de muro ajustable.",
                "usos": "Muros estructurales, paredes de concreto a la vista",
                "precio_diario": 9000,
                "precio_semanal": 45000,
                "precio_mensual": 135000,
                "disponibilidad": "Alta - Más de 2000 paneles disponibles"
            },
            {
                "nombre": "Formaletas para Losas",
                "descripcion": "Sistema de soporte para el vaciado de losas y entrepisos.",
                "especificaciones": "Puntales telescópicos, vigas principales y secundarias. Alturas desde 3 hasta 10 metros.",
                "usos": "Construcción de losas y entrepisos en edificaciones",
                "precio_diario": 11000,
                "precio_semanal": 55000,
                "precio_mensual": 165000,
                "disponibilidad": "Media - Requiere verificación para grandes áreas"
            }
        ],
        "accesorios": [
            {
                "nombre": "Tensores y tirantes para formaletas",
                "precio_semanal": 6000,
                "disponibilidad": "Alta"
            },
            {
                "nombre": "Esquineros para columnas",
                "precio_semanal": 4500,
                "disponibilidad": "Alta"
            },
            {
                "nombre": "Puntales telescópicos",
                "precio_semanal": 8000,
                "disponibilidad": "Alta"
            },
            {
                "nombre": "Desmoldante biodegradable",
                "precio_por_galon": 35000,
                "disponibilidad": "Alta"
            }
        ],
        "certificaciones": [
            "ISO 9001:2015 - Sistemas de Gestión de Calidad",
            "Certificación de resistencia de materiales",
            "Cumplimiento con normas sismo-resistentes"
        ]
    }
}

# Servicios: Información sobre servicios ofrecidos
SERVICIOS = {
    "alquiler": {
        "proceso": [
            "Contacto inicial y determinación de necesidades",
            "Evaluación técnica y recomendación de equipos",
            "Cotización y aprobación",
            "Firma de contrato y pago de depósito",
            "Entrega e instalación (opcional) en obra",
            "Asistencia técnica durante el período de alquiler",
            "Devolución del equipo y verificación",
            "Devolución del depósito"
        ],
        "requisitos": [
            "Documento de identidad o NIT de empresa",
            "Comprobante de domicilio o dirección comercial",
            "Depósito de seguridad (reembolsable)",
            "Firma de contrato de alquiler"
        ],
        "ventajas": [
            "Flexibilidad en períodos de alquiler",
            "Equipos certificados y en excelente estado",
            "Soporte técnico durante todo el período",
            "Opciones de transporte e instalación",
            "Precios competitivos y descuentos por volumen"
        ]
    },
    "transporte": {
        "zonas": {
            "urbana": {
                "tiempo_entrega": "24 horas",
                "costo_base": 80000,
                "costo_adicional": "Según volumen"
            },
            "metropolitana": {
                "tiempo_entrega": "24-48 horas",
                "costo_base": 120000,
                "costo_adicional": "Según volumen y distancia"
            },
            "regional": {
                "tiempo_entrega": "2-4 días",
                "costo_base": 200000,
                "costo_adicional": "5000 por kilómetro adicional"
            },
            "nacional": {
                "tiempo_entrega": "3-7 días",
                "costo": "Cotización personalizada"
            }
        },
        "servicios_adicionales": [
            {
                "nombre": "Entrega Express",
                "descripcion": "Entrega en el mismo día para pedidos realizados antes de las 10AM",
                "sobrecosto": "50% sobre la tarifa estándar"
            },
            {
                "nombre": "Montaje y desmontaje",
                "descripcion": "Personal calificado para instalación y retiro",
                "costo": "120000 por día/técnico"
            },
            {
                "nombre": "Supervisión técnica",
                "descripcion": "Visitas periódicas para verificar montaje y uso adecuado",
                "costo": "150000 por visita"
            }
        ]
    },
    "asesoría_técnica": {
        "servicios": [
            "Evaluación de necesidades en sitio",
            "Diseño de configuraciones de andamios",
            "Cálculo de cargas y factores de seguridad",
            "Capacitación al personal en montaje y uso seguro",
            "Supervisión de instalaciones"
        ],
        "costo": "Incluido para alquileres superiores a 2 millones de pesos"
    }
}

# Políticas: Información sobre políticas de la empresa
POLITICAS = {
    "pago": {
        "metodos_aceptados": [
            "Efectivo",
            "Transferencia bancaria",
            "Tarjetas de crédito y débito (Visa, Mastercard, American Express)",
            "PSE y pagos en línea",
            "Crédito empresarial (previa aprobación)"
        ],
        "deposito_seguridad": {
            "porcentaje": "20-30% del valor total del alquiler",
            "devolucion": "Al finalizar el contrato, previa verificación del estado del equipo"
        },
        "facturacion": {
            "tipo": "Factura electrónica",
            "datos_requeridos": "NIT/CC, dirección, razón social, correo electrónico para factura electrónica"
        }
    },
    "garantia": {
        "cobertura": "Defectos de fabricación, desgaste normal durante el uso adecuado",
        "exclusiones": "Daños por mal uso, negligencia o condiciones fuera de especificaciones",
        "procedimiento": "Notificación inmediata del problema, evaluación técnica, reparación o reemplazo sin costo"
    },
    "seguridad": {
        "normas_cumplimiento": [
            "ISO 45001:2018 - Sistemas de gestión de seguridad y salud en el trabajo",
            "Resolución 1409 de 2012 - Trabajo seguro en alturas",
            "NSR-10 - Norma Sismo Resistente colombiana"
        ],
        "capacitacion": {
            "incluida": "Capacitación básica en uso seguro",
            "adicional": "Certificación en trabajo en alturas (costo adicional)"
        },
        "inspeccion": "Revisión completa de todos los equipos antes de cada alquiler"
    },
    "devolucion": {
        "condiciones": "Equipos limpios y en condiciones similares a la entrega, considerando desgaste normal",
        "penalizaciones": "Cargos adicionales por daños, pérdidas o limpieza extraordinaria",
        "extension": "Posibilidad de extender período de alquiler con notificación previa mínima de 48 horas"
    }
}

# Descuentos y promociones
DESCUENTOS = {
    "volumen": [
        {
            "rango": "1 millón - 3 millones",
            "porcentaje": "5%"
        },
        {
            "rango": "3 millones - 7 millones",
            "porcentaje": "10%"
        },
        {
            "rango": "Más de 7 millones",
            "porcentaje": "15%"
        }
    ],
    "duracion": [
        {
            "periodo": "1-2 semanas",
            "porcentaje": "0%"
        },
        {
            "periodo": "3-4 semanas",
            "porcentaje": "10%"
        },
        {
            "periodo": "1-3 meses",
            "porcentaje": "15%"
        },
        {
            "periodo": "Más de 3 meses",
            "porcentaje": "20%"
        }
    ],
    "cliente_frecuente": {
        "criterio": "Más de 3 alquileres en el último año",
        "beneficio": "10% adicional sobre otros descuentos aplicables"
    },
    "proyectos_especiales": "Descuentos personalizados para proyectos gubernamentales, educativos o sociales"
}

# Información de contacto
CONTACTO = {
    "telefono": "(123) 456-7890",
    "celular": "+57 300 123 4567",
    "whatsapp": "+57 300 123 4567",
    "email": "info@multiandamios.com",
    "website": "www.multiandamios.com",
    "direccion": "Calle Principal #123, Ciudad",
    "horario": {
        "lunes_viernes": "8:00 AM - 6:00 PM",
        "sabado": "9:00 AM - 1:00 PM",
        "domingo": "Cerrado"
    }
}

# FAQs - Preguntas frecuentes
PREGUNTAS_FRECUENTES = [
    {
        "pregunta": "¿Cuál es el tiempo mínimo de alquiler?",
        "respuesta": "El tiempo mínimo de alquiler para la mayoría de nuestros equipos es de una semana. Sin embargo, para ciertos equipos especializados ofrecemos alquileres por día."
    },
    {
        "pregunta": "¿Incluye el servicio de montaje y desmontaje?",
        "respuesta": "El servicio básico de alquiler no incluye montaje y desmontaje, pero ofrecemos este servicio adicional con personal especializado. El costo depende de la complejidad y tamaño de la estructura."
    },
    {
        "pregunta": "¿Qué sucede si necesito extender el período de alquiler?",
        "respuesta": "Puedes extender el período de alquiler notificándonos con al menos 48 horas de anticipación, sujeto a disponibilidad. Te recomendamos contactarnos lo antes posible para asegurar la extensión."
    },
    {
        "pregunta": "¿Qué documentos necesito para alquilar equipos?",
        "respuesta": "Para personas naturales: documento de identidad y comprobante de domicilio. Para empresas: NIT, Cámara de Comercio reciente, y documento de identidad del representante legal. Todos los contratos requieren un depósito de seguridad reembolsable."
    },
    {
        "pregunta": "¿Ofrecen servicio técnico durante el período de alquiler?",
        "respuesta": "Sí, ofrecemos soporte técnico durante todo el período de alquiler. Para problemas graves que requieran reemplazo de equipos, lo gestionamos sin costo adicional si se trata de fallas no atribuibles al mal uso."
    },
    {
        "pregunta": "¿Entregan en cualquier parte del país?",
        "respuesta": "Sí, realizamos entregas a nivel nacional. Los tiempos y costos varían según la ubicación. Para zonas urbanas principales, la entrega suele ser en 24-48 horas, mientras que para zonas más remotas puede tomar entre 3-7 días."
    },
    {
        "pregunta": "¿Cómo se determina el depósito de seguridad?",
        "respuesta": "El depósito de seguridad generalmente oscila entre el 20% y el 30% del valor total del alquiler, dependiendo del tipo y cantidad de equipos. Este depósito es completamente reembolsable al finalizar el contrato, siempre que los equipos se devuelvan en buen estado."
    },
    {
        "pregunta": "¿Los equipos cuentan con certificaciones de seguridad?",
        "respuesta": "Sí, todos nuestros equipos cuentan con certificaciones nacionales e internacionales de seguridad, incluyendo ISO 9001, ISO 45001 y cumplen con todas las normativas locales de construcción y seguridad industrial."
    }
]

# Terminología específica del sector para reconocimiento de consultas
TERMINOLOGIA = {
    "andamios": ["andamio", "andamios", "estructura", "estructuras", "soporte", "soportes", "torre", "torres", "scaffold", "scaffolding"],
    "formaletas": ["formaleta", "formaletas", "encofrado", "encofrados", "molde", "moldes", "formwork", "mold", "cimbra"],
    "columnas": ["columna", "columnas", "pilar", "pilares", "poste", "postes", "column"],
    "muros": ["muro", "muros", "pared", "paredes", "tabique", "tabiques", "wall"],
    "losas": ["losa", "losas", "entrepiso", "entrepisos", "techo", "techos", "plancha", "planchas", "slab", "floor"],
    "precio": ["precio", "precios", "costo", "costos", "valor", "tarifa", "tarifas", "cotización", "cotizaciones", "cuánto cuesta", "cuanto vale", "precio por", "rate", "cost"],
    "alquiler": ["alquilar", "alquiler", "rentar", "renta", "arrendar", "arriendo", "lease", "rent", "rental"],
    "entrega": ["entrega", "envío", "despacho", "transporte", "transportar", "llevar", "delivery", "shipping"],
    "seguridad": ["seguridad", "seguro", "protección", "riesgo", "peligro", "norma", "normas", "certificado", "certificación", "safety", "security"]
}

# Información de la empresa
EMPRESA = {
    "nombre": "MultiAndamios S.A.S.",
    "fundacion": 2010,
    "mision": "Proporcionar soluciones seguras y eficientes para trabajos en altura y estructuras temporales, contribuyendo al éxito de los proyectos de construcción con equipos de alta calidad y servicio excepcional.",
    "vision": "Ser la empresa líder en soluciones de acceso temporal y encofrados en la región, reconocida por la calidad de sus productos, innovación constante y compromiso con la seguridad.",
    "cobertura": "Nacional con oficinas principales en Bogotá, Medellín, Cali y Barranquilla",
    "clientes_destacados": [
        "Constructora ABC",
        "Edificaciones XYZ",
        "Proyectos Urbanos S.A.",
        "Infraestructura Nacional Ltda.",
        "Desarrollos Residenciales 123"
    ]
}
