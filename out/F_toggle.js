var horizontal;

document.addEventListener('DOMContentLoaded', function() {
    var fontToggle = document.getElementById('fontToggle');
    var tab = document.getElementById('tab');
    console.log('1. Skrypt załadowany');
    console.log('2. Czy ustawiono dużą czcionkę?', tab);

    function checkWindowDimensions() {
        var width = window.innerWidth;
        var height = window.innerHeight;
        horizontal = width > height;
        console.log('Szerokość okna:', width);
        console.log('Wysokość okna:', height);
        console.log('Czy okno jest bardziej poziome?', horizontal);
        updateFontSize();
    }

    function updateFontSize() {
        if (fontToggle.classList.contains('active') && horizontal) {
            tab.classList.remove('default', 'large');
            tab.classList.add('huge');
        } else if (fontToggle.classList.contains('active') || horizontal) {
            tab.classList.remove('default', 'huge');
            tab.classList.add('large');
        } else {
            tab.classList.remove('large', 'huge');
            tab.classList.add('default');
        }
    }

    if (tab) {
        // Sprawdź stan localStorage przy ładowaniu strony
        console.log(localStorage.getItem('largeFont'));
        if (localStorage.getItem('largeFont') === 'true') {
            console.log('3. dotarłam tu');
            if (fontToggle) {
                fontToggle.classList.add('active');
                fontToggle.textContent = 'ON';
            }
            updateFontSize();
        }
        console.log('3. largeFont:', localStorage.getItem('largeFont'));

        // Zmień klasę, tekst i zapisz stan w localStorage przy kliknięciu przycisku
        if (fontToggle) {
            fontToggle.addEventListener('click', function() {
                fontToggle.classList.toggle('active');
                if (fontToggle.classList.contains('active')) {
                    fontToggle.textContent = 'ON';
                    localStorage.setItem('largeFont', 'true');
                } else {
                    fontToggle.textContent = 'OFF';
                    localStorage.setItem('largeFont', 'false');
                }
                updateFontSize();
            });
        }

        // Sprawdź proporcje okna przy ładowaniu strony
        checkWindowDimensions();

        // Sprawdź proporcje okna przy zmianie rozmiaru okna
        window.addEventListener('resize', checkWindowDimensions);
    } else {
        console.error('Element tab nie istnieje.');
    }
});

