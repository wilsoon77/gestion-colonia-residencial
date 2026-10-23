/**
 * Animaciones Fluidas de Scroll & Navegación - Residencial Las Encinas de Fraijanes
 * Implementación de alto rendimiento acelerada por GPU (60fps/120fps)
 */
(function() {
    function initScrollAnimations() {
        // 1. Asignación de retardo escalonado (stagger) para grupos de tarjetas
        const staggerGroups = document.querySelectorAll('.scroll-stagger-group');
        staggerGroups.forEach(group => {
            const items = group.querySelectorAll('.scroll-reveal');
            items.forEach((item, index) => {
                if (!item.style.getPropertyValue('--reveal-delay')) {
                    item.style.setProperty('--reveal-delay', `${index * 130}ms`);
                }
            });
        });

        // 2. Elementos que se revelan con scroll
        const revealElements = document.querySelectorAll('.scroll-reveal');
        if (revealElements.length === 0) return;

        // Función para revelar un elemento con animación fluida
        const revealItem = (el) => {
            if (!el.classList.contains('is-revealed')) {
                el.classList.add('is-revealed');
            }
        };

        // 3. Uso de IntersectionObserver para disparar animación en cuanto entran en pantalla
        if ('IntersectionObserver' in window) {
            const observerOptions = {
                root: null,
                rootMargin: '0px 0px -30px 0px',
                threshold: 0.04
            };

            const revealObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        revealItem(entry.target);
                        observer.unobserve(entry.target);
                    }
                });
            }, observerOptions);

            revealElements.forEach(el => {
                revealObserver.observe(el);
            });
        } else {
            // Fallback para navegadores antiguos sin IntersectionObserver
            revealElements.forEach(revealItem);
        }

        // 4. Verificación complementaria al hacer scroll (para máxima fluidez y fiabilidad)
        let scrollTicking = false;
        const checkVisibilityOnScroll = () => {
            const triggerZone = window.innerHeight - 30;
            revealElements.forEach(el => {
                if (!el.classList.contains('is-revealed')) {
                    const rect = el.getBoundingClientRect();
                    if (rect.top <= triggerZone && rect.bottom >= 0) {
                        revealItem(el);
                    }
                }
            });
            scrollTicking = false;
        };

        window.addEventListener('scroll', () => {
            if (!scrollTicking) {
                window.requestAnimationFrame(checkVisibilityOnScroll);
                scrollTicking = true;
            }
        }, { passive: true });

        // 5. Elevación dinámica del Navbar flotante al hacer scroll
        const navbar = document.querySelector('.landing-navbar');
        if (navbar) {
            const handleNavbarScroll = () => {
                if (window.scrollY > 30) {
                    navbar.classList.add('is-scrolled');
                } else {
                    navbar.classList.remove('is-scrolled');
                }
            };
            window.addEventListener('scroll', handleNavbarScroll, { passive: true });
            handleNavbarScroll();
        }

        // 6. ScrollSpy para resaltar sección activa en la barra de navegación
        const navLinks = document.querySelectorAll('.landing-nav-link[href^="#"]');
        const sections = Array.from(navLinks)
            .map(link => {
                try {
                    const target = document.querySelector(link.getAttribute('href'));
                    return target ? { link, target } : null;
                } catch (e) {
                    return null;
                }
            })
            .filter(item => item !== null);

        if (sections.length > 0 && 'IntersectionObserver' in window) {
            const spyObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const id = entry.target.getAttribute('id');
                        navLinks.forEach(link => {
                            if (link.getAttribute('href') === `#${id}`) {
                                link.classList.add('active');
                            } else {
                                link.classList.remove('active');
                            }
                        });
                    }
                });
            }, {
                root: null,
                rootMargin: '-20% 0px -65% 0px',
                threshold: 0
            });

            sections.forEach(item => spyObserver.observe(item.target));
        }

        // 7. Desplazamiento suave al hacer clic en enlaces del navbar con offset arquitectónico
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                if (!targetId || targetId === '#') return;

                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    const navbarOffset = 90;
                    const elementPosition = targetElement.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - navbarOffset;

                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    // Ejecutar cuando el DOM esté listo, o inmediatamente si ya cargó
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initScrollAnimations);
    } else {
        initScrollAnimations();
    }
})();
