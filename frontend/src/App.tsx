import { ChakraProvider, Flex, Text, Box } from '@chakra-ui/react';
import FileUpload from './features/fileUpload/FileUpload';
import { colors } from './shared/ui/theme/colors';

export default function App() {
    return (
        <ChakraProvider>
            <Box position="relative" w="100%" minH="100vh">
                <Text
                    position="absolute"
                    top="10px"
                    left="30px"
                    fontSize="xl"
                    fontWeight="bold"
                    color={colors.text}
                >
                    SmartNotes
                </Text>

                <Flex
                    minH="100vh"
                    w="100%"
                    bg={colors.bg}
                    color={colors.text}
                    justify="center"
                    align="center"
                >
                    <FileUpload />
                </Flex>
            </Box>
        </ChakraProvider>
    )
}
