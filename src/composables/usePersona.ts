import {
  personas,
  activePersonaId,
  showPersonaModal,
  personaForm,
  editingPersonaId,
  activePersona,
} from "../store";

export function usePersona() {
  function loadPersonas() {
    try {
      const stored = localStorage.getItem("user_personas");
      personas.value = stored ? JSON.parse(stored) : [];
      activePersonaId.value = localStorage.getItem("active_persona_id") || "";
    } catch {
      personas.value = [];
      activePersonaId.value = "";
    }
  }

  function savePersonas() {
    try {
      localStorage.setItem("user_personas", JSON.stringify(personas.value));
      localStorage.setItem("active_persona_id", activePersonaId.value);
    } catch {}
  }

  function openPersonaModal() {
    showPersonaModal.value = true;
    editingPersonaId.value = null;
    personaForm.value = {
      id: "",
      name: "",
      gender: "Male",
      appearance: "",
      personality: "",
      avatar_emoji: "🧑",
      avatar_image: "",
    };
  }

  function editPersona(p: any) {
    editingPersonaId.value = p.id;
    personaForm.value = { ...p };
  }

  function savePersonaForm() {
    const form = personaForm.value;
    if (!form.name.trim()) return;

    if (editingPersonaId.value) {
      const idx = personas.value.findIndex(
        (p: any) => p.id === editingPersonaId.value
      );
      if (idx >= 0) {
        personas.value[idx] = { ...form, id: editingPersonaId.value };
      }
    } else {
      const newPersona = {
        ...form,
        id: crypto.randomUUID(),
        created_at: Date.now(),
      };
      personas.value.push(newPersona);
      if (!activePersonaId.value) {
        activePersonaId.value = newPersona.id;
      }
    }
    savePersonas();
    editingPersonaId.value = null;
    personaForm.value = {
      id: "",
      name: "",
      gender: "Male",
      appearance: "",
      personality: "",
      avatar_emoji: "🧑",
      avatar_image: "",
    };
  }

  function deletePersona(id: string) {
    personas.value = personas.value.filter((p: any) => p.id !== id);
    if (activePersonaId.value === id) {
      activePersonaId.value =
        personas.value.length > 0 ? personas.value[0].id : "";
    }
    savePersonas();
    if (editingPersonaId.value === id) {
      editingPersonaId.value = null;
      personaForm.value = {
        id: "",
        name: "",
        gender: "Male",
        appearance: "",
        personality: "",
        avatar_emoji: "🧑",
      };
    }
  }

  function setActivePersona(id: string) {
    activePersonaId.value = id;
    savePersonas();
  }

  function getPersonaPayload() {
    const p = activePersona.value;
    if (!p) return undefined;
    return {
      name: p.name,
      gender: p.gender,
      appearance: p.appearance,
      personality: p.personality,
    };
  }

  function cancelEditing() {
    editingPersonaId.value = null;
    personaForm.value = {
      id: "",
      name: "",
      gender: "Male",
      appearance: "",
      personality: "",
      avatar_emoji: "🧑",
      avatar_image: "",
    };
  }

  return {
    loadPersonas,
    openPersonaModal,
    editPersona,
    savePersonaForm,
    deletePersona,
    setActivePersona,
    getPersonaPayload,
    cancelEditing,
  };
}
