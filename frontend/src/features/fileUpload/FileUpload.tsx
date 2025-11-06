import { useState } from 'react';
import { Box, Button, Text, Icon, Flex, VStack, HStack, CloseButton, useToast } from '@chakra-ui/react';
import { FiUploadCloud } from 'react-icons/fi';
import { colors } from '../../shared/ui/theme/colors';
import { uploadImages, generatePdf, downloadPdf } from '../../api/api';

export default function FileUpload() {
    const [files, setFiles] = useState<File[]>([]);
    const [isDragging, setIsDragging] = useState(false);
    const [hovered, setHovered] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const toast = useToast();

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const newFiles = Array.from(e.target.files);
            const combined = [...files, ...newFiles].slice(0, 10);
            setFiles(combined);
        }
    };

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(false);
        const dropped = Array.from(e.dataTransfer.files).slice(0, 10);
        setFiles(dropped);
    };

    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => setIsDragging(false);

    const handleRemoveFile = (index: number) => {
        setFiles(files.filter((_, i) => i !== index));
    };

    const handleUpload = async () => {
        if (files.length === 0) {
            toast({
                title: 'Файлы не выбраны',
                description: 'Пожалуйста, выберите хотя бы один файл.',
                status: 'warning',
                duration: 2000,
                isClosable: true,
                position: 'bottom-left',
            });
            return;
        }
        if (files.length > 10) {
            toast({
                title: 'Слишком много файлов',
                description: 'Максимум 10 файлов за раз.',
                status: 'warning',
                duration: 2000,
                isClosable: true,
                position: 'bottom-left',
            });
            return;
        }

        try {
            setIsLoading(true);
            const uploadRes = await uploadImages(files);
            const payload = {
                request_id: uploadRes.request_id,
                images_data: uploadRes.processed_images,
                title: "Мои заметки с доски"
            };
            const pdfRes = await generatePdf(payload);
            await await downloadPdf(pdfRes.pdf_url.split('/').pop()!);
            toast({
                title: 'Файл успешно сгенерирован',
                description: 'PDF готов и скачан.',
                status: 'success',
                duration: 2000,
                isClosable: true,
                position: 'bottom-left',
            });
        } catch (err: unknown) {
            console.error(err);
            const description =
                err instanceof Error ? err.message : 'Не удалось обработать файлы';

            toast({
                title: 'Ошибка при обработке',
                description,
                status: 'error',
                duration: 2000,
                isClosable: true,
                position: 'bottom-left',
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Box
            minH="calc(100vh - 60px)"
            w="100%"
            display="flex"
            alignItems="center"
            justifyContent="center"
            bg={colors.bg}
            color={colors.text}
            p="30px"
        >
            <Flex w="100%" h="70vh" gap="30px">
                <Box
                    flex="1"
                    bg={colors.accent}
                    borderRadius="lg"
                    display="flex"
                    alignItems="flex-end"
                    justifyContent="flex-start"
                    position="relative"
                    p={6}
                    overflow="hidden"
                    cursor="pointer"
                    onMouseEnter={() => setHovered(true)}
                    onMouseLeave={() => setHovered(false)}
                >
                    <Box
                        color="white"
                        textAlign="left"
                        position="absolute"
                        bottom="10px"
                        left="20px"
                        transition="all 0.4s ease"
                        transform={hovered ? 'translateY(-160px)' : 'translateY(0)'}
                    >
                        <Text fontWeight="bold" fontSize="3xl" transition="0.4s">
                            SmartNotes
                        </Text>
                    </Box>

                    <Box color="white" textAlign="left" position="absolute">
                        <Text
                            fontSize="18"
                            opacity={hovered ? 1 : 0}
                            transform={hovered ? 'translateY(0px)' : 'translateY(40px)'}
                            transition="all 0.4s ease"
                            maxW="700px"
                        >
                            SmartNotes - это инструмент для преобразования конспекта из рукописного формата в электронный.<br />
                            Добавьте от 1 до 10 изображений в соседнее поле и нажмите кнопку "Загрузить файл".<br />
                            После обработки система вернёт Вам файл с конспектом в .pdf формате.
                        </Text>
                    </Box>
                </Box>

                <Box flex="1" textAlign="center" display="flex" flexDirection="column">
                    <Box
                        as="label"
                        htmlFor="file-upload"
                        onDrop={handleDrop}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        border="2px dashed"
                        borderColor={colors.border}
                        borderRadius="lg"
                        flex="1"
                        cursor="pointer"
                        bg={isDragging ? colors.border : 'transparent'}
                        transition="0.2s"
                        display="flex"
                        flexDirection="column"
                        alignItems="center"
                        justifyContent="center"
                    >
                        <input
                            id="file-upload"
                            type="file"
                            multiple
                            onChange={handleFileChange}
                            style={{ display: 'none' }}
                        />
                        <Icon as={FiUploadCloud} boxSize={16} color={colors.accent} mb={6} />
                        {files.length > 0 ? (
                            <VStack spacing={1}>
                                {files.map((f, i) => (
                                    <HStack>
                                        <Text key={i} color={colors.accent} fontWeight="semibold" isTruncated>
                                            {f.name}
                                        </Text>
                                        <CloseButton size="sm" onClick={() => handleRemoveFile(i)} />
                                    </HStack>
                                ))}
                            </VStack>
                        ) : (
                            <>
                                <Text fontWeight="medium" fontSize="lg">
                                    Перетащи сюда файлы
                                </Text>
                                <Text fontSize="sm" color="gray.600">
                                    или кликни, чтобы выбрать (до 10)
                                </Text>
                            </>
                        )}
                    </Box>

                    <Button
                        mt={6}
                        w="100%"
                        bg={colors.accent}
                        color="white"
                        _hover={{ bg: colors.border }}
                        onClick={handleUpload}
                        py={6}
                        fontSize="lg"
                        isLoading={isLoading}
                        loadingText="Обработка..."
                    >
                        Загрузить файлы
                    </Button>
                </Box>
            </Flex>
        </Box>
    );
}
