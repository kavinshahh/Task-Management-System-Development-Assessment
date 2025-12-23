import { useEffect, useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import { AuthContext } from "../context/AuthContext";
import Input from "../components/Input";
import Button from "../components/Button";
import Card from "../components/Card";
import TaskItem from "../components/TaskItem";
import "./Dashboard.css";

export default function Dashboard() {
  const { token, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState(1);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchTasks = async () => {
    try {
      const res = await api.get("/tasks/", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setTasks(res.data);
    } catch (err) {
      console.error("Failed to load tasks", err);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleAddTask = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await api.post(
        "/tasks/",
        { title, description, priority },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setTasks((prev) => [...prev, res.data]);
      setTitle("");
      setDescription("");
      setPriority(1);
    } catch (err) {
      console.error("Failed to create task", err);
      setError("Failed to create task");
    } finally {
      setLoading(false);
    }
  };

  const handleToggleComplete = async (taskId) => {
    const task = tasks.find((t) => t.id === taskId);
    if (!task) return;

    try {
      const res = await api.put(
        `/tasks/${taskId}`,
        { ...task, complete: !task.complete },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? res.data : t))
      );
    } catch (err) {
      console.error("Failed to update task", err);
      alert("Failed to update task");
    }
  };

  const handleDeleteTask = async (taskId) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this task?"
    );

    if (!confirmDelete) return;

    try {
      await api.delete(`/tasks/${taskId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      setTasks((prev) => prev.filter((task) => task.id !== taskId));
    } catch (err) {
      console.error("Failed to delete task", err);
      alert("Failed to delete task");
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const completedCount = tasks.filter((t) => t.complete).length;

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div className="dashboard-header-content">
          <div>
            <h1 className="dashboard-header-title">Task Dashboard</h1>
            <p className="dashboard-header-subtitle">
              Manage your tasks efficiently
            </p>
          </div>
          <Button variant="danger" onClick={handleLogout}>
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9" />
            </svg>
            Logout
          </Button>
        </div>
      </div>

      <div className="dashboard-content">
        <Card title="Create New Task" subtitle="Add a new task to your list">
          {error && (
            <div className="dashboard-error-banner">
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              {error}
            </div>
          )}

          <form onSubmit={handleAddTask} className="dashboard-form">
            <Input
              label="Task Title"
              placeholder="Enter task title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />

            <Input
              label="Description"
              placeholder="Enter task description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />

            <div className="dashboard-form-row">
              <div className="dashboard-select-wrapper">
                <label className="dashboard-label">Priority</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(Number(e.target.value))}
                  className="dashboard-select"
                >
                  <option value={1}>Low</option>
                  <option value={2}>Medium</option>
                  <option value={3}>High</option>
                </select>
              </div>

              <div className="dashboard-button-wrapper">
                <Button type="submit" loading={loading} fullWidth>
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <line x1="12" y1="5" x2="12" y2="19" />
                    <line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                  Add Task
                </Button>
              </div>
            </div>
          </form>
        </Card>

        <div className="dashboard-tasks-section">
          <div className="dashboard-tasks-section-header">
            <h2 className="dashboard-tasks-title">Your Tasks</h2>
            <span className="dashboard-task-count">
              {tasks.length} {tasks.length === 1 ? "task" : "tasks"}
              {tasks.length > 0 && ` • ${completedCount} completed`}
            </span>
          </div>

          {tasks.length === 0 ? (
            <div className="dashboard-empty-state">
              <svg
                width="64"
                height="64"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#d1d5db"
                strokeWidth="1.5"
              >
                <path d="M9 11l3 3L22 4M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
              </svg>
              <p className="dashboard-empty-state-text">No tasks yet</p>
              <p className="dashboard-empty-state-subtext">
                Create your first task to get started
              </p>
            </div>
          ) : (
            <div>
              {tasks.map((task) => (
                <TaskItem
                  key={task.id}
                  task={task}
                  onDelete={handleDeleteTask}
                  onToggleComplete={handleToggleComplete}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}