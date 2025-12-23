import "./TaskItem.css";

export default function TaskItem({ task, onDelete, onToggleComplete }) {
  const getPriorityLabel = (priority) => {
    switch (priority) {
      case 1:
        return "Low";
      case 2:
        return "Medium";
      case 3:
        return "High";
      default:
        return "Unknown";
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 1:
        return "task-priority-low";
      case 2:
        return "task-priority-medium";
      case 3:
        return "task-priority-high";
      default:
        return "";
    }
  };

  return (
    <div className={`task-item ${task.complete ? "task-item-completed" : ""}`}>
      <div className="task-item-main">
        <button
          onClick={() => onToggleComplete(task.id)}
          className={`task-checkbox ${task.complete ? "task-checkbox-checked" : ""}`}
          aria-label={task.complete ? "Mark as incomplete" : "Mark as complete"}
        >
          <span className="task-checkbox-inner">
            {task.complete && (
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polyline points="20 6 9 17 4 12" />
              </svg>
            )}
          </span>
        </button>

        <div className="task-item-content">
          <div className="task-item-header">
            <h3 className={`task-item-title ${task.complete ? "task-item-title-completed" : ""}`}>
              {task.title}
            </h3>
            <span className={`task-priority-badge ${getPriorityColor(task.priority)}`}>
              <span className="task-priority-dot"></span>
              {getPriorityLabel(task.priority)}
            </span>
          </div>

          {task.description && (
            <p className={`task-item-description ${task.complete ? "task-item-description-completed" : ""}`}>
              {task.description}
            </p>
          )}

          {task.complete && (
            <div className="task-complete-badge">
              <svg
                width="12"
                height="12"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <circle cx="12" cy="12" r="10" />
                <path
                  d="M9 12l2 2 4-4"
                  fill="none"
                  stroke="white"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              Completed
            </div>
          )}
        </div>
      </div>

      <button
        onClick={() => onDelete(task.id)}
        className="task-delete-button"
        aria-label="Delete task"
      >
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polyline points="3 6 5 6 21 6" />
          <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
          <line x1="10" y1="11" x2="10" y2="17" />
          <line x1="14" y1="11" x2="14" y2="17" />
        </svg>
      </button>
    </div>
  );
}