// Обновление статистики каждые 30 секунд
async function updateStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const data = await response.json();

        if (data.success) {
            // Здесь можно обновлять данные на странице
            console.log('Статистика обновлена:', data.data);
        }
    } catch (error) {
        console.error('Ошибка обновления статистики:', error);
    }
}

// Обновление каждые 30 секунд
setInterval(updateStatistics, 30000);

// Модальные окна и формы
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация модальных окон
    const editButtons = document.querySelectorAll('.btn-edit');
    editButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const studentId = this.dataset.id;
            const response = await fetch(`/api/students/${studentId}`);
            const data = await response.json();

            if (data.success) {
                // Заполнить форму редактирования
                document.getElementById('editFullname').value = data.data.fullname || '';
                document.getElementById('editTgid').value = data.data.tgid || '';
                document.getElementById('editIsActive').checked = data.data.isactive;
                document.getElementById('editGroup').value = data.data.Group || '';
                document.getElementById('editForm').dataset.id = studentId;

                // Показать модальное окно
                const modal = new bootstrap.Modal(document.getElementById('editModal'));
                modal.show();
            }
        });
    });

    // Сохранение изменений
    document.getElementById('saveChanges').addEventListener('click', async function() {
        const studentId = document.getElementById('editForm').dataset.id;
        const formData = {
            fullname: document.getElementById('editFullname').value,
            tgid: parseInt(document.getElementById('editTgid').value) || null,
            isactive: document.getElementById('editIsActive').checked,
            Group: document.getElementById('editGroup').value
        };

        const response = await fetch(`/api/students/${studentId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            location.reload();
        } else {
            alert('Ошибка при сохранении');
        }
    });
});