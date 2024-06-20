async function deleteItem(type, name) {
    const response = await fetch(`/entity?entity=${encodeURIComponent(name)}&type=${type}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    }); 

    console.log(response);

    if (response.ok) {
      location.reload();
      document.getElementById(type).focus()

    } else {
      const result = await response.json();
      alert(`Failed to delete ${type}: ${result.message}`);
    }
  }

  async function addItem(type) {
    const newItem = document.getElementById(type).value;

    const response = await fetch(`/entity?entity=${encodeURIComponent(newItem)}&type=${type}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (response.ok) {
      location.reload();
    } else {
      const result = await response.json();
      alert(`Failed to add ${type}: ${result.message}`);
    }
  }