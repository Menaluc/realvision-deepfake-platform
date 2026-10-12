import { useEffect, useRef } from "react";

// Plays a local video file through a temporary object URL
export function VideoPreview({ file }: { file: File }) {
    const videoRef = useRef<HTMLVideoElement>(null);

    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        const url = URL.createObjectURL(file);
        video.src = url;

        return () => {
            video.pause();
            video.removeAttribute("src");
            video.load();
            URL.revokeObjectURL(url);
        };
    }, [file]);

    return (
        <div className="video-box">
            <video ref={videoRef} controls playsInline />
        </div>
    );
}
