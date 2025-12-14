"use client";

import { useState, useEffect } from "react";
import Image from 'next/image'
import toast from "react-hot-toast";


interface DetectionResponse {
  image_id: string
  timestamp: string
  detections: Detection[]
  summary: Summary
  annotated_image: string
}

interface Detection {
  class: string
  confidence: number
  bbox: number[]
}

interface Summary {
  helmet_count: number
  no_helmet_count: number
}


export default function Home() {
    const [activeSection, setActiveSection] = useState<"detection" | "reports">("detection");
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [responseData, setResponseData] = useState<DetectionResponse | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [pdfReports, setPdfReports] = useState<{ url: string; name: string }[]>([]);
    const [reportLoading, setReportLoading] = useState<boolean>(false);

    // for now getting only the .jpeg base64 annotated image
    const imageUrl = responseData ? `data:image/jpeg;base64,${responseData.annotated_image}` : null;

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setSelectedFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!selectedFile) return;
        setLoading(true);
        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            const response = await fetch("http://localhost:8000/api/v1/detect", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const errorText = await response.text();
                const shortError = errorText.length > 200 ? errorText.slice(0, 200) + "..." : errorText;
                toast.error(`Upload failed: ${shortError}`);
                setLoading(false);
                setResponseData(null);
                return;
            }

            const data = await response.json();
            if (!data.annotated_image || !data.detections || !data.summary) {
                toast.error("Invalid image or server error. Please upload a valid image.");
                setResponseData(null);
                setLoading(false);
                return;
            }

            console.log("Response data:", data);
            // for now gettting only the .jpeg base64 annotated image
            setResponseData(data);
            toast.success("File uploaded and processed successfully!");
        } catch (error) {
            toast.error("An error occurred while uploading the file.");
            console.error("Error uploading file:", error);
        } finally {
            setLoading(false);
        }

    };

    useEffect(() => {
        const generateReport = async () => {
            if (!responseData) return;
            setReportLoading(true);
            try {
                const response = await fetch("http://localhost:8000/api/v1/report", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(responseData),
                })

                if (!response.ok) {
                    const errorText = await response.text();
                    const shortError = errorText.length > 200 ? errorText.slice(0, 200) + "..." : errorText;
                    toast.error(`Report generation failed: ${shortError}`);
                    setReportLoading(false);
                    return;
                }

                const data = await response.json();
                if (!data.report_url) {
                    toast.error("Report generation failed. No report URL returned.");
                    setReportLoading(false);
                    return;
                }

                setPdfReports((prevReports) => [
                    ...prevReports,
                    { url: data.report_url, name: `report_${responseData.image_id}.pdf` },
                ]);
                toast.success("Report generated successfully!");

            } catch (error) {
                toast.error("An error occurred while generating the report.");
                console.error("Error generating report:", error);
            } finally {
                setReportLoading(false);    
        }
        };

        if (responseData) {
            generateReport();
        }
    }, [responseData]);
    

    return (
        <div className="flex h-screen bg-neutral-100">
        {/* Sidebar */}
        <aside className="w-1/3 min-w-[260px] max-w-[400px] bg-neutral-900 shadow-xl flex flex-col p-8 justify-between overflow-y-auto min-h-0">
            <div>
                <div className="mb-8 flex flex-col gap-6">
                    <span className="text-2xl font-bold text-white tracking-tight mb-2 ">PPE Vision Detectio System</span>
                    <div className="mt-2 bg-neutral-800 rounded-lg p-4 text-white text-sm font-medium shadow flex flex-col items-center">
                        <div>1. <b>Load an image</b></div>
                        <div className="text-2xl my-1">↓</div>
                        <div>2. <b>Identify compliants/violations</b></div>
                        <div className="text-2xl my-1">↓</div>
                        <div>3. <b>Check &amp; download the reports</b></div>
                    </div>
                </div>
                <div className="flex flex-col gap-4">
                    <button
                        className={`py-3 px-6 rounded-xl text-lg font-medium transition shadow ${
                            activeSection === "detection"
                                ? "bg-white text-neutral-900 shadow-lg"
                                : "bg-neutral-800 text-neutral-300 hover:bg-neutral-700"
                        }`}
                        onClick={() => setActiveSection("detection")}
                    >
                        Detection
                    </button>
                    <button
                        className={`py-3 px-6 rounded-xl text-lg font-medium transition shadow ${
                            activeSection === "reports"
                                ? "bg-white text-neutral-900 shadow-lg"
                                : "bg-neutral-800 text-neutral-300 hover:bg-neutral-700"
                        }`}
                        onClick={() => setActiveSection("reports")}
                    >
                        Reports
                    </button>
                </div>
            </div>
            <div className="flex flex-col items-center mt-8 w-full">
                <Image
                    src="/the_watch_dogs_1.png"
                    alt="Watch Dog Logo"
                    width={500}
                    height={500}
                    className="w-full h-auto object-contain mb-2 max-w-[220px]"
                    priority
                />
                <span className="text-white text-center text-lg opacity-80 break-words w-full">
                    The Watch Dogs are watching you !!!</span>
            </div>
        </aside>
        {/* Main Content */}
        <main className="w-2/3 flex justify-center items-center bg-neutral-100">
            <div className="w-full max-w-3xl bg-white rounded-3xl shadow-2xl p-10 min-h-[70vh] max-h-[90vh] flex flex-col overflow-auto">
            {activeSection === "detection" && (
                <div className="flex flex-col h-full gap-8">
                {/* Upper Panel */}
                <section className="bg-neutral-50 rounded-2xl shadow-md p-8 mb-2 flex flex-col items-center gap-6">
                    <h1 className="text-3xl font-semibold text-neutral-900 mb-2">Detection</h1>
                    <label className="block w-60 px-6 py-3 bg-white border-2 border-neutral-300 rounded-xl shadow cursor-pointer hover:shadow-lg transition text-center">
                    <span className="text-neutral-800 font-medium">Choose File</span>
                    <input
                        type="file"
                        accept="image/*"
                        onChange={handleFileChange}
                        className="hidden"
                    />
                    </label>
                    {selectedFile && (
                    <span className="text-neutral-600 text-sm truncate w-60 text-center">
                        Selected File: {selectedFile.name}
                    </span>
                    )}
                    <button
                    className="w-60 py-3 px-6 bg-neutral-900 text-white rounded-xl font-semibold hover:bg-black transition shadow"
                    onClick={handleUpload}
                    disabled={!selectedFile || loading}
                    >
                    {loading ? "Uploading..." : "Upload Image"}
                    </button>
                </section>
                {/* Lower Panel */}
                <section className="flex-1 flex flex-col items-center justify-start bg-neutral-200 rounded-2xl shadow-inner border border-neutral-300 p-6 w-full overflow-auto max-h-[400px]">
                    {responseData && responseData.summary && responseData.detections ? (
                        <>
                        {/* Info above the image */}
                        <div className="mb-4 w-full max-w-xl bg-white rounded-xl shadow p-4">
                            <div className="flex flex-wrap gap-4 justify-between text-neutral-700 text-sm">
                            <div>
                                <span className="font-semibold">Image ID:</span> {responseData.image_id}
                            </div>
                            <div>
                                <span className="font-semibold">Timestamp:</span>{" "}
                                {new Date(responseData.timestamp).toLocaleString()}
                            </div>
                            </div>
                            <div className="mt-4 flex flex-wrap gap-8 text-sm text-neutral-800">
                            <div>
                                <span className="font-semibold">Compliants:</span> {responseData.summary.helmet_count}
                            </div>
                            <div>
                                <span className="font-semibold">Violations:</span> {responseData.summary.no_helmet_count}
                            </div>
                            </div>
                            <div className="mt-4">
                            <span className="font-semibold text-neutral-900 text-sm">Detections:</span>
                            <ul className="list-disc list-inside ml-4 text-neutral-800">
                                {responseData.detections.map((det, idx) => (
                                <li key={idx} className="mb-1">
                                    <span className="font-medium">{det.class}</span>{" "}
                                    <span className="text-neutral-700">
                                    (confidence: {(det.confidence * 100).toFixed(1)}%, bbox: [
                                    {det.bbox.join(", ")}])
                                    </span>
                                </li>
                                ))}
                            </ul>
                            </div>
                        </div>
                        {/* Image */}
                        {imageUrl && (
                            <Image
                            src={imageUrl}
                            alt="Uploaded"
                            className="max-h-[350px] max-w-full rounded-xl shadow"
                            width={580}
                            height={400}
                            />
                        )}
                        </>
                    ) : responseData && (!responseData.summary || !responseData.detections) ? (
                        <div className="text-red-600 text-lg font-semibold">
                        Invalid image or server error. Please upload a valid image.
                        </div>
                    ) : (
                        <span className="text-neutral-400 text-lg">No image loaded</span>
                    )}
                    </section>
                </div>
            )}
            {activeSection === "reports" && (
                <section className="flex flex-col h-full justify-center items-center w-full">
                <h1 className="text-3xl font-semibold text-neutral-900 mb-4">Reports</h1>
                {pdfReports.length === 0 ? (
                    <p className="text-neutral-600 text-lg">No reports generated yet.</p>
                ) : (
                    <ul className="w-full max-w-xl flex flex-col gap-4">
                    {pdfReports.map((report, idx) => (
                        <li key={idx} className="bg-neutral-50 rounded-xl shadow p-4 flex flex-col gap-2">
                        <span className="font-semibold text-neutral-800">{report.name}</span>
                        <a
                            href={report.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-700 hover:underline"
                        >
                            View PDF Report
                        </a>
                        <iframe
                            src={report.url}
                            className="w-full h-64 rounded border mt-2"
                            title={`PDF Report ${idx + 1}`}
                        />
                        </li>
                    ))}
                    </ul>
                )}
                </section>
            )}
            </div>
        </main>
        </div>
    );
}

