document.getElementById('activeBtn').addEventListener('click', function(){
    const button = document.getElementById('activeBtn');

    if (button.innerText == 'Ativar Serviço') {
        button.innerText = 'Desativar Serviço';
    } else {
        button.innerText = 'Ativar Serviço';
    }
});