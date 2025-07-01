function validateDiasMinimos() {
    const diasMinimosInput = document.getElementById('id_dias_minimos_renta');
    const precioDiarioInput = document.getElementById('id_precio_diario');
    
    if (!diasMinimosInput || !precioDiarioInput) {
        return;
    }
    
    const diasMinimos = parseInt(diasMinimosInput.value);
    
    // Validar que los días mínimos sean al menos 1
    if (diasMinimos < 1) {
        diasMinimosInput.setCustomValidity('Los días mínimos de renta deben ser al menos 1.');
    } else {
        diasMinimosInput.setCustomValidity('');
    }
    
    // Mostrar información sobre el sistema de precios
    updatePriceInfo(diasMinimos, parseFloat(precioDiarioInput.value));
}

function updatePriceInfo(diasMinimos, precioDiario) {
    let infoDiv = document.getElementById('price-info');
    
    if (!infoDiv) {
        // Crear el div de información si no existe
        infoDiv = document.createElement('div');
        infoDiv.id = 'price-info';
        infoDiv.style.cssText = 'margin-top: 10px; padding: 10px; background-color: #e7f3ff; border: 1px solid #bee5eb; border-radius: 4px; font-size: 13px;';
        
        const diasField = document.querySelector('.field-dias_minimos_renta');
        if (diasField) {
            diasField.appendChild(infoDiv);
        }
    }
    
    if (diasMinimos && precioDiario && diasMinimos > 0 && precioDiario > 0) {
        const precioMinimo = diasMinimos * precioDiario;
        infoDiv.innerHTML = `
            <strong>Sistema de precio diario:</strong><br>
            • Precio por día: $${precioDiario.toLocaleString()}<br>
            • Mínimo de días: ${diasMinimos}<br>
            • Precio mínimo de renta: $${precioMinimo.toLocaleString()}<br>
            • Los clientes solo podrán rentar en múltiplos de ${diasMinimos} días
        `;
    } else {
        infoDiv.innerHTML = '<em>Complete los campos para ver la información de precios</em>';
    }
}

// Función para inicializar el comportamiento del nuevo sistema
function initializePricingSystem() {
    console.log('initializePricingSystem: Iniciando sistema de precio diario...');
    
    // Configurar validación de días mínimos
    const diasMinimosInput = document.getElementById('id_dias_minimos_renta');
    const precioDiarioInput = document.getElementById('id_precio_diario');
    
    if (diasMinimosInput) {
        diasMinimosInput.addEventListener('input', validateDiasMinimos);
        diasMinimosInput.addEventListener('change', validateDiasMinimos);
        console.log('initializePricingSystem: Listener agregado a dias_minimos_renta');
    }
    
    if (precioDiarioInput) {
        precioDiarioInput.addEventListener('input', validateDiasMinimos);
        precioDiarioInput.addEventListener('change', validateDiasMinimos);
        console.log('initializePricingSystem: Listener agregado a precio_diario');
    }
    
    // Validación inicial
    validateDiasMinimos();
    
    console.log('initializePricingSystem: Sistema configurado correctamente');
}

// Ejecutar cuando el DOM está listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePricingSystem);
} else {
    initializePricingSystem();
}

// También ejecutar cuando se carga completamente la ventana
window.addEventListener('load', function() {
    setTimeout(initializePricingSystem, 200);
});

// Ejecutar si estamos en una página de Django admin que usa AJAX
if (typeof django !== 'undefined' && django.jQuery) {
    django.jQuery(document).ready(function() {
        initializePricingSystem();
    });
}
