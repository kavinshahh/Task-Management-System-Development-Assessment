export default function Button({ 
  children, 
  variant = "primary", 
  size = "md",
  fullWidth = false,
  icon: Icon,
  loading = false,
  ...props 
}) {
  const variantStyles = {
    primary: {
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
      color: "#fff",
      border: "none",
    },
    secondary: {
      background: "#f3f4f6",
      color: "#374151",
      border: "1px solid #d1d5db",
    },
    danger: {
      background: "#ef4444",
      color: "#fff",
      border: "none",
    },
    ghost: {
      background: "transparent",
      color: "#667eea",
      border: "1px solid #667eea",
    },
  };

  const sizeStyles = {
    sm: {
      padding: "8px 16px",
      fontSize: "13px",
    },
    md: {
      padding: "12px 24px",
      fontSize: "14px",
    },
    lg: {
      padding: "14px 28px",
      fontSize: "16px",
    },
  };

  return (
    <button
      style={{
        ...styles.base,
        ...variantStyles[variant],
        ...sizeStyles[size],
        ...(fullWidth ? { width: "100%" } : {}),
        ...(loading || props.disabled ? styles.disabled : {}),
      }}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading ? (
        <span style={styles.loader}></span>
      ) : (
        <>
          {Icon && <Icon size={18} style={styles.icon} />}
          {children}
        </>
      )}
    </button>
  );
}

const styles = {
  base: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    fontWeight: "500",
    borderRadius: "8px",
    cursor: "pointer",
    transition: "all 0.2s",
    outline: "none",
    fontFamily: "inherit",
  },
  disabled: {
    opacity: 0.6,
    cursor: "not-allowed",
  },
  icon: {
    flexShrink: 0,
  },
  loader: {
    width: "16px",
    height: "16px",
    border: "2px solid #ffffff",
    borderTopColor: "transparent",
    borderRadius: "50%",
    animation: "spin 0.6s linear infinite",
  },
};