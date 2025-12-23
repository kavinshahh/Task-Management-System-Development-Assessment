export default function Card({ 
  children, 
  title, 
  subtitle,
  footer,
  hoverable = false,
  ...props 
}) {
  return (
    <div
      style={{
        ...styles.card,
        ...(hoverable ? styles.hoverable : {}),
      }}
      {...props}
    >
      {(title || subtitle) && (
        <div style={styles.header}>
          {title && <h3 style={styles.title}>{title}</h3>}
          {subtitle && <p style={styles.subtitle}>{subtitle}</p>}
        </div>
      )}
      <div style={styles.content}>{children}</div>
      {footer && <div style={styles.footer}>{footer}</div>}
    </div>
  );
}

const styles = {
  card: {
    background: "#fff",
    borderRadius: "12px",
    padding: "24px",
    boxShadow: "0 1px 3px rgba(0, 0, 0, 0.1)",
    transition: "all 0.3s",
  },
  hoverable: {
    cursor: "pointer",
  },
  header: {
    marginBottom: "16px",
  },
  title: {
    fontSize: "18px",
    fontWeight: "600",
    color: "#111827",
    margin: "0 0 4px 0",
  },
  subtitle: {
    fontSize: "14px",
    color: "#6b7280",
    margin: 0,
  },
  content: {
    fontSize: "14px",
    color: "#374151",
  },
  footer: {
    marginTop: "16px",
    paddingTop: "16px",
    borderTop: "1px solid #e5e7eb",
  },
};