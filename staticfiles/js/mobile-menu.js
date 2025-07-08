// JavaScript para menú hamburguesa responsive

document.addEventListener('DOMContentLoaded', function() {
    // Verificar si estamos en móvil
    if (window.innerWidth <= 768) {
        createMobileMenu();
        initializeMobileMenu();
    }
    
    // Reinicializar en cambio de tamaño de ventana
    window.addEventListener('resize', function() {
        handleResize();
    });
});

function createMobileMenu() {
    // Verificar si ya existe el botón
    if (document.querySelector('.mobile-menu-toggle')) {
        return;
    }
    
    // Crear botón hamburguesa
    const menuToggle = document.createElement('button');
    menuToggle.className = 'mobile-menu-toggle';
    menuToggle.innerHTML = '☰';
    menuToggle.setAttribute('aria-label', 'Abrir menú');
    menuToggle.setAttribute('type', 'button');
    
    // Crear overlay
    const overlay = document.createElement('div');
    overlay.className = 'mobile-menu-overlay';
    overlay.setAttribute('aria-hidden', 'true');
    
    // Modificar navegación existente
    const mainNav = document.querySelector('.main-navigation');
    if (mainNav) {
        // Crear header del menú móvil
        const header = document.createElement('div');
        header.className = 'mobile-header';
        header.innerHTML = '<h1>🏗️ MultiAndamios</h1>';
        
        // Crear botón de cerrar
        const closeButton = document.createElement('button');
        closeButton.className = 'mobile-menu-close';
        closeButton.innerHTML = '×';
        closeButton.setAttribute('aria-label', 'Cerrar menú');
        closeButton.setAttribute('type', 'button');
        
        // Agregar elementos al menú
        header.appendChild(closeButton);
        mainNav.insertBefore(header, mainNav.firstChild);
        
        // Agregar clases a los enlaces existentes
        const navLinks = mainNav.querySelectorAll('a');
        navLinks.forEach(link => {
            if (!link.classList.contains('nav-button')) {
                link.classList.add('nav-button');
            }
        });
    }
    
    // Agregar elementos al DOM
    document.body.appendChild(menuToggle);
    document.body.appendChild(overlay);
    
    console.log('Menú móvil creado exitosamente');
}

function initializeMobileMenu() {
    // Esperar un momento para asegurar que los elementos estén en el DOM
    setTimeout(() => {
        const menuToggle = document.querySelector('.mobile-menu-toggle');
        const menuOverlay = document.querySelector('.mobile-menu-overlay');
        const menuClose = document.querySelector('.mobile-menu-close');
        const mainNav = document.querySelector('.main-navigation');
        
        // Event listeners
        if (menuToggle) {
            menuToggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                toggleMobileMenu();
            });
        }
        
        if (menuOverlay) {
            menuOverlay.addEventListener('click', function(e) {
                e.preventDefault();
                closeMobileMenu();
            });
        }
        
        if (menuClose) {
            menuClose.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                closeMobileMenu();
            });
        }
        
        // Cerrar menú al hacer clic en un enlace
        if (mainNav) {
            const navLinks = mainNav.querySelectorAll('a');
            navLinks.forEach(link => {
                link.addEventListener('click', function() {
                    // Pequeño delay para permitir que la navegación inicie
                    setTimeout(() => {
                        closeMobileMenu();
                    }, 100);
                });
            });
        }
        
        // Cerrar menú con tecla Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeMobileMenu();
            }
        });
        
        // Prevenir scroll cuando el menú está abierto
        document.addEventListener('touchmove', function(e) {
            const mainNav = document.querySelector('.main-navigation');
            if (mainNav && mainNav.classList.contains('active')) {
                // Permitir scroll solo dentro del menú
                if (!mainNav.contains(e.target)) {
                    e.preventDefault();
                }
            }
        }, { passive: false });
        
        console.log('Event listeners del menú móvil inicializados');
    }, 100);
}

function toggleMobileMenu() {
    const mainNav = document.querySelector('.main-navigation');
    const overlay = document.querySelector('.mobile-menu-overlay');
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    
    if (mainNav && overlay && menuToggle) {
        const isOpen = mainNav.classList.contains('active');
        
        if (isOpen) {
            closeMobileMenu();
        } else {
            openMobileMenu();
        }
    }
}

function openMobileMenu() {
    const mainNav = document.querySelector('.main-navigation');
    const overlay = document.querySelector('.mobile-menu-overlay');
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    
    if (mainNav && overlay && menuToggle) {
        mainNav.classList.add('active');
        overlay.classList.add('active');
        
        // Cambiar icono del botón
        menuToggle.innerHTML = '×';
        menuToggle.setAttribute('aria-label', 'Cerrar menú');
        
        // Prevenir scroll del body
        document.body.style.overflow = 'hidden';
        
        // Focus en el primer enlace del menú para accesibilidad
        const firstLink = mainNav.querySelector('a');
        if (firstLink) {
            setTimeout(() => {
                firstLink.focus();
            }, 300);
        }
        
        console.log('Menú móvil abierto');
    }
}

function closeMobileMenu() {
    const mainNav = document.querySelector('.main-navigation');
    const overlay = document.querySelector('.mobile-menu-overlay');
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    
    if (mainNav && overlay && menuToggle) {
        mainNav.classList.remove('active');
        overlay.classList.remove('active');
        
        // Restaurar icono del botón
        menuToggle.innerHTML = '☰';
        menuToggle.setAttribute('aria-label', 'Abrir menú');
        
        // Restaurar scroll del body
        document.body.style.overflow = '';
        
        console.log('Menú móvil cerrado');
    }
}

function handleResize() {
    const currentWidth = window.innerWidth;
    
    if (currentWidth > 768) {
        // Desktop - remover elementos móviles
        closeMobileMenu();
        removeMobileElements();
    } else {
        // Móvil - crear elementos si no existen
        if (!document.querySelector('.mobile-menu-toggle')) {
            createMobileMenu();
            initializeMobileMenu();
        }
    }
}

function removeMobileElements() {
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    const overlay = document.querySelector('.mobile-menu-overlay');
    const mobileHeader = document.querySelector('.mobile-header');
    
    if (menuToggle) {
        menuToggle.remove();
    }
    
    if (overlay) {
        overlay.remove();
    }
    
    if (mobileHeader) {
        mobileHeader.remove();
    }
    
    // Restaurar scroll del body
    document.body.style.overflow = '';
    
    console.log('Elementos móviles removidos para vista desktop');
}

// Función para debug - remover en producción
function debugMobileMenu() {
    console.log('=== DEBUG MENÚ MÓVIL ===');
    console.log('Ancho de ventana:', window.innerWidth);
    console.log('Botón hamburguesa:', document.querySelector('.mobile-menu-toggle'));
    console.log('Overlay:', document.querySelector('.mobile-menu-overlay'));
    console.log('Navegación principal:', document.querySelector('.main-navigation'));
    console.log('Header móvil:', document.querySelector('.mobile-header'));
}

// Exportar funciones para uso global si es necesario
window.mobileMenu = {
    toggle: toggleMobileMenu,
    open: openMobileMenu,
    close: closeMobileMenu,
    debug: debugMobileMenu
};
