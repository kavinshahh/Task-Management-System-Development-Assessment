export default function Input({ 
  label, 
  error, 
  icon: Icon,
  ...props 
}) {
  return (
    <div style={styles.container}>
      {label && <label style={styles.label}>{label}</label>}
      <div style={styles.inputWrapper}>
        {Icon && (
          <div style={styles.iconWrapper}>
            <Icon size={20} style={styles.icon} />
          </div>
        )}
        <input
          style={{
            ...styles.input,
            ...(Icon ? styles.inputWithIcon : {}),
            ...(error ? styles.inputError : {}),
          }}
          {...props}
        />
      </div>
      {error && <span style={styles.error}>{error}</span>}
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    gap: "6px",
    width: "100%",
  },
  label: {
    fontSize: "14px",
    fontWeight: "500",
    color: "#374151",
    marginBottom: "2px",
  },
  inputWrapper: {
    position: "relative",
    width: "100%",
  },
  iconWrapper: {
    position: "absolute",
    left: "12px",
    top: "50%",
    transform: "translateY(-50%)",
    display: "flex",
    alignItems: "center",
    pointerEvents: "none",
  },
  icon: {
    color: "#9ca3af",
  },
  input: {
    width: "100%",
    padding: "12px 14px",
    fontSize: "14px",
    border: "1px solid #d1d5db",
    borderRadius: "8px",
    outline: "none",
    transition: "all 0.2s",
    backgroundColor: "#fff",
    boxSizing: "border-box",
  },
  inputWithIcon: {
    paddingLeft: "42px",
  },
  inputError: {
    borderColor: "#ef4444",
  },
  error: {
    fontSize: "12px",
    color: "#ef4444",
    marginTop: "2px",
  },
};