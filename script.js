
        const form = document.getElementById('updateForm');
        const columnEntries = document.getElementById('columnEntries');
        const addColumnBtn = document.getElementById('addColumn');
        const submitButton = form.querySelector('button[type="submit"]');
        const responseDiv = document.getElementById('response');

        // Function to add a new column entry
        function addColumnEntry() {
            const entry = document.createElement('div');
            entry.className = 'column-entry';
            entry.innerHTML = `
                <input type="text" placeholder="Column Name" class="column-name" required>
                <input type="text" placeholder="Value" class="column-value">
                <button type="button" onclick="this.parentElement.remove()">Remove</button>
            `;
            columnEntries.appendChild(entry);
        }

        // Add initial column entry
        addColumnEntry();

        // Add more column entries on button click
        addColumnBtn.addEventListener('click', addColumnEntry);

        // Handle form submission
        form.addEventListener('submit', async function(event) {
            event.preventDefault();

            submitButton.disabled = true;
            submitButton.textContent = 'Submitting...';
            responseDiv.style.display = 'none';
            responseDiv.classList.remove('success', 'error');

            const formData = {
                id: document.getElementById('id').value,
                columns: {}
            };

            const columnNames = document.querySelectorAll('.column-name');
            const columnValues = document.querySelectorAll('.column-value');
            columnNames.forEach((nameInput, index) => {
                const name = nameInput.value.trim();
                const value = columnValues[index].value.trim() || null;
                if (name) {
                    formData.columns[name] = value;
                }
            });

            try {
                const response = await fetch('http://your-api-endpoint/update', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                const result = await response.json();

                responseDiv.textContent = result.message;
                responseDiv.classList.add('success');
                responseDiv.style.display = 'block';

                form.reset();
                columnEntries.innerHTML = '';
                addColumnEntry(); // Reset with one entry
            } catch (error) {
                responseDiv.textContent = 'Error: ' + error.message;
                responseDiv.classList.add('error');
                responseDiv.style.display = 'block';
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = 'Submit Update';
            }
        });
