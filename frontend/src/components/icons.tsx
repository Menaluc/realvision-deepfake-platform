import type { ReactNode } from "react";

function Icon({ strokeWidth = 1.8, children }: { strokeWidth?: number; children: ReactNode }) {
    return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={strokeWidth}
            strokeLinecap="round" strokeLinejoin="round">
            {children}
        </svg>
    );
}

export const EyeIcon = () => (
    <Icon>
        <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7Z" />
        <circle cx="12" cy="12" r="3.2" />
    </Icon>
);

export const UploadIcon = () => (
    <Icon>
        <path d="M7 16a4 4 0 0 1-.88-7.9A5 5 0 0 1 15.9 6H16a4 4 0 0 1 1 7.87" />
        <path d="M12 12v6" />
        <path d="m9 15 3-3 3 3" />
    </Icon>
);

export const WarningIcon = () => (
    <Icon strokeWidth={2}>
        <path d="m21.7 18-8-14a2 2 0 0 0-3.4 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-3Z" />
        <path d="M12 9v4" />
        <path d="M12 17h.01" />
    </Icon>
);

export const CheckIcon = () => (
    <Icon strokeWidth={2}>
        <circle cx="12" cy="12" r="10" />
        <path d="m9 12 2 2 4-4" />
    </Icon>
);

export const FileIcon = () => (
    <Icon>
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <path d="M14 2v6h6" />
    </Icon>
);

export const ClockIcon = () => (
    <Icon>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 7v5l3 2" />
    </Icon>
);

export const DatabaseIcon = () => (
    <Icon>
        <ellipse cx="12" cy="5" rx="8" ry="3" />
        <path d="M4 5v14c0 1.66 3.58 3 8 3s8-1.34 8-3V5" />
        <path d="M4 12c0 1.66 3.58 3 8 3s8-1.34 8-3" />
    </Icon>
);

export const ArrowLeftIcon = () => (
    <Icon strokeWidth={2}>
        <path d="M19 12H5" />
        <path d="m12 19-7-7 7-7" />
    </Icon>
);

export const CloseIcon = () => (
    <Icon strokeWidth={2}>
        <path d="M18 6 6 18" />
        <path d="m6 6 12 12" />
    </Icon>
);
