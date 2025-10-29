import { useState } from 'react';
import { Box, Button, Text, Icon, Flex } from '@chakra-ui/react';
import { FiUploadCloud } from 'react-icons/fi';
import { colors } from '../../shared/ui/theme/colors';

export default function FileUpload() {
    const [file, setFile] = useState<File | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [hovered, setHovered] = useState(false);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) setFile(e.target.files[0]);
    }

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]);
    }

    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(true);
    }

    const handleDragLeave = () => setIsDragging(false);

    const handleUpload = () => {
        if (!file) return alert('Пожалуйста, выбери файл!');
        alert(`Файл "${file.name}" готов к загрузке`);
    }

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
                        transform={hovered ? 'translateY(-130px)' : 'translateY(0)'}
                    >
                        <Text
                            size="md"
                            fontWeight="bold"
                            fontSize="3xl"
                            transition="0.4s"
                        >
                            SmartNotes
                        </Text>
                    </Box>

                    <Box
                        color="white"
                        textAlign="left"
                        position="absolute"
                    >
                        <Text
                            fontSize="18"
                            opacity={hovered ? 1 : 0}
                            transform={hovered ? 'translateY(0px)' : 'translateY(40px)'}
                            transition="all 0.4s ease"
                            maxW="700px"
                        >
                            SmartNotes - это инструмент для преобразования конспекта из рукописного формата в электронный.<br />
                            Добавьте изображение в соседнее поле и нажмите кнопку "Загрузить файл".<br />
                            После обработки система вернёт Вам файл с конспектом в .docx формате.
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
                            onChange={handleFileChange}
                            style={{ display: 'none' }}
                        />
                        <Icon as={FiUploadCloud} boxSize={16} color={colors.accent} mb={6} />
                        {file ? (
                            <Text color={colors.accent} fontWeight="semibold" isTruncated>
                                {file.name}
                            </Text>
                        ) : (
                            <>
                                <Text fontWeight="medium" fontSize="lg">Перетащи сюда файл</Text>
                                <Text fontSize="sm" color="gray.600">
                                    или кликни, чтобы выбрать
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
                    >
                        Загрузить файл
                    </Button>
                </Box>
            </Flex>
        </Box>
    )
}
