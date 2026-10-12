import type { ReactNode } from "react";
import type { VideoInfo } from "../types/analysis";
import { formatBytes, formatDuration, formatFileType } from "../utils/format";
import { ClockIcon, DatabaseIcon, FileIcon } from "./icons";

function MetaItem({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
    return (
        <div className="meta-item">
            {icon}
            <div>
                <div className="meta-label">{label}</div>
                <div className="meta-value">{value}</div>
            </div>
        </div>
    );
}

export function MetaGrid({ video }: { video: VideoInfo }) {
    return (
        <div className="meta-grid">
            <MetaItem icon={<FileIcon />} label="File name" value={video.name} />
            <MetaItem icon={<ClockIcon />} label="Duration" value={formatDuration(video.duration)} />
            <MetaItem icon={<FileIcon />} label="File type" value={formatFileType(video.type)} />
            <MetaItem icon={<DatabaseIcon />} label="File size" value={formatBytes(video.size)} />
        </div>
    );
}
